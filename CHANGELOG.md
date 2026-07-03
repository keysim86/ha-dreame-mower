# Changelog

## [1.1.31] - 2026-07-03

### Fixed
- `device.py`: bezpiecznik OOM w `_build_map_data_from_zones_json` — uszkodzone dane `boundary` z chmury mogły spowodować alokację gigantycznego rastra numpy (gigabajty RAM); dodano limit 4 mln pikseli, ten sam co w builderze ścieżki

## [1.1.30] - 2026-07-03

Regresja z 1.1.29: po restarcie HA w momencie, gdy robot spał, sensory Battery Level / State / Charging Status pozostawały trwale "niedostępne" (mimo że lawn_mower działał). Przyczyna wielowarstwowa zdiagnozowana na żywo przez API HA.

### Fixed
- `sensor.py`: encje sensorów tworzone są teraz dynamicznie — jeśli initial fetch properties padnie (robot w uśpieniu przy starcie HA), sensory powstaną automatycznie, gdy tylko property pojawi się w danych (push MQTT lub udany poll); wcześniej wymagały reloadu integracji przy obudzonym robocie
- `device.py`: polling ponawia teraz brakujące default properties — dotąd po `_ready` odpytywane były tylko propy już obecne w `self.data`, więc nieudany initial fetch zostawiał je puste na zawsze
- `dreame/types.py`: `CleaningHistory.__eq__` — porównanie było po tożsamości obiektów, więc każde odświeżenie historii raportowało "Cleaning History Changed" i wyzwalało lawinę przebudów mapy oraz pobrań plików z chmury (timeouty po 15 s blokujące pętlę aktualizacji)
- `device.py`: odświeżanie historii po sesji działa też na A1 Pro — warunek `task_status == COMPLETED` (nigdy nie raportowany przez ten firmware) rozszerzony o `docked`

### Changed
- `device.py`: usunięta przebudowa mapy co 30 s i odświeżanie historii co 60 s podczas koszenia (z 1.1.29) — chmura publikuje ślad GPS dopiero po zakończeniu sesji, więc generowały wyłącznie timeouty MAP batch obciążające integrację; mapa przebudowuje się raz po każdej realnej zmianie historii

## [1.1.29] - 2026-07-03

Diagnoza na żywo podczas koszenia (API HA + logi INFO) — trzy odkrycia: (1) `running` jest False na A1 Pro w trakcie koszenia (status spoza listy odkurzaczowej), (2) chmura ma 318 zdarzeń sesji, z czego 17 przerwanych z `duration==0` — aplikacja je liczy (317), integracja odfiltrowywała (301), (3) chmura publikuje plik śladu GPS dopiero PO zakończeniu sesji, więc pozycji live podczas koszenia nie da się uzyskać z tego API.

### Fixed
- `device.py`: przebudowa mapy co 30 s podczas koszenia nie działała — bramka sprawdzała `running` (False na A1 Pro w trakcie koszenia); teraz aktywne koszenie wykrywane jako `started && !docked`
- `device.py`: licznik sesji — zliczane są też sesje przerwane (`duration==0`, `area>0`, np. błąd "Trapped") z deduplikacją po timestampie startu; Mowing Count pokaże ~318 zamiast 301 (aplikacja: 317)
- `device.py`: Current Zone przy zadokowaniu — dok stoi tuż poza wielokątami stref (`strefa=None` w logach); pozycja jest teraz przyciągana do najbliższej strefy w promieniu ~2 m
- `button.py`: dostępność przycisków Mow Zone/skróty/backup — predykat `started && !docked` (poprzedni `running` z 1.1.28 pozwalałby klikać strefy w trakcie koszenia)
- `device.py`: odświeżanie historii co 60 s tylko podczas aktywnego koszenia (nie przy zadokowanym — `started` jest tam True przez quirk firmware)

### Changed
- `device.py`: podczas aktywnego koszenia pozycja robota NIE jest nanoszona ze starego śladu (marker przy doku byłby mylący, gdy robot jest w polu) — pojawia się po zakończeniu sesji; log "Zero-duration event props" (INFO, 2 pierwsze zdarzenia) do dalszej diagnozy różnicy powierzchni

### Known issues
- Pozycja robota live podczas koszenia niedostępna — chmura Dreame publikuje ślad GPS dopiero po zakończeniu sesji; pozycja i Current Zone aktualizują się po każdej sesji
- Total Mowed Area ~55 367 m² vs ~58 324 m² w aplikacji (~5%) — suma pól `area` wszystkich 318 zdarzeń chmury daje wartość integracji; źródło wyższej wartości aplikacji nieustalone (prawdopodobnie serwerowy akumulator Dreame niedostępny przez to API)

## [1.1.28] - 2026-07-02

### Fixed
- `button.py`: przyciski Mow Zone1/2/3 (oraz skróty i backup mapy) były nieaktywne, gdy robot stał zadokowany — A1 Pro po pełnym naładowaniu raportuje `charging_status = not_charging` przy `state = charging_completed`, przez co `started` pozostaje True i `available_fn` blokował przyciski; dostępność oparta teraz o faktyczny ruch (`running`), więc koszenie strefy można uruchomić z doku

### Changed
- `device.py`: `_populate_stats_from_history` używa piidów z `property_mapping` (`CLEANING_TIME`/`CLEANED_AREA`/`CLEANING_START_TIME`) zamiast zahardkodowanych 2/3/4 — odporne na różnice modeli (dla A1 Pro wartości identyczne: 2/3/8)
- `device.py`: dodano log diagnostyczny "Stats history breakdown" — surowa liczba zdarzeń chmury vs sesje z `duration>0`, sesje z `duration==0` (i ile z nich ma `area>0`), aktualne wartości siid:12 oraz suma powierzchni łącznie z sesjami zerowymi; pozwala ustalić źródło różnicy między HA a aplikacją (np. 301 vs 317)

### Known issues
- Liczba koszeń / łączna powierzchnia wciąż mogą być niższe niż w aplikacji Dreame: sam firmware A1 Pro (siid:12) zaniża je względem aplikacji, a chmura przechowuje ograniczoną liczbę zdarzeń sesji. Integracja pokazuje maksimum z (licznik firmware, historia chmury) — najlepszą dostępną wartość. Log "Stats history breakdown" (przy DEBUG dla `custom_components.dreame_mower`) pokazuje pełny rozkład.

## [1.1.27] - 2026-07-02

### Fixed
- `device.py`: mapa pokazywała jedną sztuczną strefę "Trawnik" zamiast rzeczywistych stref — `_try_build_map_from_batch` sklejał wszystkie klucze `MAP.0-255` i parsował tylko pierwszy dokument JSON (często starą/pustą mapę); teraz każdy klucz parsowany osobno, a spośród kandydatów wybierana jest mapa z największą liczbą stref (aktywna map2 z Zone 1/2/3)
- `device.py`: gdy jeden klucz zawiera listę kilku zapisanych map, wybierany jest wpis z niepustymi `mowingAreas` (największą liczbą stref), nie pierwszy z brzegu
- `device.py`: pozycja robota nie aktualizowała się podczas koszenia — historia sesji odświeżała się tylko po zakończonym zadaniu, więc mapa w kółko budowała się ze STAREJ sesji; teraz historia odświeża się co 60 s podczas koszenia, a mapa przebudowywana jest też raz po zakończeniu sesji (domyka ślad i pozycję)

### Added
- `device.py`: `_overlay_robot_position` — na mapie stref (batch MAP) nanoszona jest pozycja robota z ostatniego punktu GPS śladu oraz wyliczany `robot_segment` (strefa, w której robot faktycznie stoi)
- `device.py`: `current_zone` korzysta teraz z `robot_segment` niezależnie od `lidar_navigation` — Current Zone pokazuje rzeczywistą strefę (także po zadokowaniu, jeśli dok leży w strefie); fallback na `active_segments` podczas koszenia bez zmian
- Logi diagnostyczne: "MAP kandydat (klucz N): X stref: [...]" i "Pozycja robota z historii: (x, y), strefa=N" — pozwalają zweryfikować w logach HA, co zwraca chmura

## [1.1.26] - 2026-07-02

### Fixed
- `device.py`: **regresja mapy z v1.1.24** — brakujący import `Point` powodował `NameError` w `_build_map_data_from_path_json`, przez co mapa z historii w ogóle się nie budowała (Current Map "brak aktywności", Saved Map niedostępny, Current Zone niedostępny); dodano import
- `device.py`: statystyki (`CLEANING_COUNT`, `TOTAL_CLEANING_TIME`, `TOTAL_CLEANED_AREA`) — cykliczny odczyt properties nadpisywał wartości z historii chmury z powrotem zaniżonymi licznikami firmware (siid:12); dodano guard w `_handle_properties` (przyjmuj tylko wartości większe, dla `FIRST_CLEANING_DATE` wcześniejsze) oraz scalanie per-property przez max/min w `_populate_stats_from_history`
- `device.py`: statystyki odświeżają się teraz razem z historią koszenia (przy połączeniu i po każdym ukończonym zadaniu), a nie tylko raz przy starcie; parsowanie pojedynczych rekordów historii odporne na błędne dane

### Changed
- Nazwy encji: Clean/Cleaning/Cleaned → Mow/Mowing/Mowed (np. "Mowing Count", "Total Mowed Area", "Total Mowing Time", "First Mowing Date", "Scheduled Mow", "Mowing Mode") — zmienione tylko nazwy wyświetlane, entity_id bez zmian
- `translations/en.json`: przeniesiono 39 zmian terminologii cleaning→mowing z v1.1.23, które trafiły tylko do `strings.json` (HA dla custom integracji czyta wyłącznie `translations/*.json`, więc dotąd nie były widoczne w UI)
- `translations/pl.json`: stany kosiarki po polsku — "Koszenie" zamiast "Sprzątanie/Czyszczenie" (status, task_status, task_type, CleanGenius, błędy tras); terminologia mopa/odkurzacza w nieużywanych przez kosiarkę kluczach bez zmian

## [1.1.25] - 2026-07-02

### Fixed
- `device.py`: `current_zone` — fallback na `active_segments` był wewnątrz bloku `if lidar_navigation`, który dla A1 Pro (ma `MAP_SAVING` → `lidar_navigation=False`) był pomijany w całości; przeniesiono fallback poza ten blok — sensor Current Zone / Current Zone ID działa teraz poprawnie podczas koszenia

## [1.1.24] - 2026-07-02

### Fixed
- `device.py`: statystyki (`CLEANING_COUNT`, `TOTAL_CLEANED_AREA`, `TOTAL_CLEANING_TIME`) — `_populate_stats_from_history` zawsze uruchamia się i nadpisuje wartości siid:12 gdy historia chmury raportuje ≥ tyle samo sesji; eliminuje rozbieżność między HA a aplikacją Dreame (firmware A1 Pro zaniża liczniki)
- `device.py`: brak pozycji robota na mapie historycznej — `_build_map_data_from_path_json` ustawia teraz `robot_position` na ostatni znany punkt GPS ścieżki (aktualizacja co ~30 s podczas koszenia)
- `device.py`: `current_zone` (sensor Current Zone / Current Zone ID) — dodano fallback dla A1 Pro bez real-time `robot_segment`: gdy koszona jest dokładnie jedna strefa lub mapa ma tylko jeden segment, zwraca ten segment jako aktywny; eliminuje stan "niedostępny" podczas koszenia

## [1.1.23] - 2026-07-02

### Added
- `sensor.battery_level` — dodano atrybut `icon` z dynamiczną ikoną baterii (ładowanie / poziom); port upstream v1.8.4

### Changed
- `strings.json` — zmieniono terminologię w wartościach wyświetlanych użytkownikowi: `cleaning`/`Cleaning` → `mowing`/`Mowing` (np. "Zone mowing", "Standard mowing"); klucze JSON bez zmian, entity IDs nie pękają; port upstream v1.8.7

## [1.1.22] - 2026-05-28

### Added
- `sensor.current_zone_id` — ID aktualnie koszonej strefy (dostępny gdy kosiarka kosi konkretną strefę)
- `sensor.current_zone_state` — nazwa aktualnie koszonej strefy
- Dynamiczne przyciski `button.mow_zone_<id>` — uruchamianie koszenia wybranej strefy z poziomu HA
- Automatyczny retry połączenia z chmurą po rozłączeniu (60 s opóźnienie)

### Fixed
- Kamera mapy (`Current Map`) — A1 Pro przechowuje historię sesji jako ścieżkę GPS (`map[0].data`), nie definicje stref; dodano parser `_build_map_data_from_path_json` który rysuje tę ścieżkę jako widzialną mapę ze strefą "Trawnik"
- `device.py`: `state` — A1 Pro wysyła `STATE=CHARGING` nawet po pełnym naładowaniu; dodano override: gdy `battery=100%` → `CHARGING_COMPLETED`; eliminuje niespójność między sensorami State i Charging Status
- `device.py`: `_try_build_map_from_batch` — batch MAP zwraca pustą mapę (`mowingAreas.value=[]`); teraz prawidłowy fallback do historii sesji
- `config_flow.py`: błąd `AttributeError: property 'config_entry' has no setter` w nowszych wersjach HA; usunięto ręczne przypisanie w `__init__`

## [1.1.22-beta.6] - 2026-05-28

### Fixed
- `config_flow.py`: `DreameMowerOptionsFlowHandler.__init__` próbował ustawiać `self.config_entry` który jest read-only property w nowszych wersjach HA (`AttributeError: property has no setter`); usunięto ręczne `__init__` — HA wstrzykuje `config_entry` automatycznie do `OptionsFlow`
- `device.py`: `_build_map_data_from_path_json` — zmieniono `saved_map=True` na `history_map=True`; przy `saved_map=True` renderer pomijał obliczanie `bounds` dla wymiarów mapy co mogło powodować błędy renderowania; `history_map=True` używa prawidłowej ścieżki gdzie `bounds` jest obliczane przez `_calculate_bounds`

## [1.1.22-beta.5] - 2026-05-28

### Added
- `device.py`: `_build_map_data_from_path_json` — nowy parser formatu historii A1 Pro; historia sesji przechowuje ścieżkę GPS (`map[0].data` = lista par `[x,y]`), nie definicje stref; parser rysuje tę ścieżkę jako widzialną mapę (jeden syntetyczny segment "Trawnik" z narysowaną trasą)
- `device.py`: `_try_use_last_history_map` — próbuje obu formatów: najpierw stref, potem ścieżki GPS

## [1.1.22-beta.4] - 2026-05-28

### Fixed
- `device.py`: `state` — A1 Pro wysyła `STATE=CHARGING` nawet po pełnym naładowaniu; dodano override analogiczny do `charging_status`: gdy `battery=100%` → zwróć `CHARGING_COMPLETED` zamiast `CHARGING`; eliminuje niespójność między sensorami State i Charging Status

## [1.1.22-beta.3] - 2026-05-28

### Fixed
- `device.py`: `_try_use_last_history_map` — ten sam bug co w batch: mapa bez stref nie powinna być ustawiana; teraz gdy historia też ma `mowingAreas.value=[]`, próbuje kolejnej sesji zamiast zatrzymywać się na pustej mapie

### Debug
- `device.py`: tymczasowy log WARNING z pierwszymi 300 znakami każdego pobranego pliku historii — do diagnozy struktury JSON stref

## [1.1.22-beta.2] - 2026-05-28

### Fixed
- `device.py`: `_try_build_map_from_batch` — batch MAP zwraca mapę z pustym `mowingAreas.value=[]` (mapa bazowa bez stref); poprzednio kończyło się na tej mapie i nigdy nie wywoływano `_try_use_last_history_map`; teraz gdy mapa jest pusta, fallback do historii sesji gdzie A1 Pro przechowuje faktyczne strefy koszenia
- `device.py`: `_build_map_data_from_zones_json` — obsługa `mowingAreas` zarówno gdy jest `dict` z kluczem `value` jak i bezpośrednio listą

## [1.1.22-beta.1] - 2026-05-28

### Debug
- `device.py`: tymczasowe logi WARNING w `_build_map_data_from_zones_json` — służyły do diagnozy pustej mapy na A1 Pro (usunięte w beta.2)

## [1.1.21] - 2026-05-28

### Added
- `sensor.current_zone_id` — ID aktualnie koszonej strefy (dostępny gdy kosiarka kosi konkretną strefę)
- `sensor.current_zone_state` — nazwa aktualnie koszonej strefy (np. "Zone A", "Trawnik przedni")
- Dynamiczne przyciski `button.mow_zone_<id>` dla każdej strefy z mapy — umożliwiają uruchomienie koszenia wybranej strefy z poziomu HA; nazwy stref pobierane z API chmury
- Automatyczny retry połączenia z chmurą — gdy kosiarka rozłączy się (disconnected), coordinator odczeka 60 s i automatycznie spróbuje wznowić połączenie

## [1.1.20] - 2026-05-28

### Fixed
- `device.py`: usunięto `_property_changed()` po załadowaniu mapy z chmury — wywoływanie w złym momencie mogło przerywać pipeline aktualizacji encji MQTT (Battery Level, Charging Status, State pokazywały "niedostępny")
- `device.py`: usunięto `_request_properties` po historii koszenia — dodatkowe zapytanie cloud mogło blokować połączenie MQTT powodując niedostępność sensorów live

## [1.1.19] - 2026-05-28

### Fixed
- `device.py`: `docked` — przywrócono logikę z v1.1.14; warunek `NOT_CHARGING + battery=100%` powodował że kosiarka raportowała "zadokowana" gdy stała bezczynnie na trawniku z pełną baterią (np. po koszeniu bez powrotu do stacji)
- `device.py`: `_populate_stats_from_history` — zmieniono limit zapytania z 2000 na 500; API Dreame Cloud może zwracać błąd przy zbyt dużym limicie co powodowało że statystyki nigdy się nie aktualizowały

## [1.1.18] - 2026-04-25

### Fixed
- `device.py`: `_populate_stats_from_history` — paginacja przez `time_end` nie działała (API ignoruje ten parametr i zwraca te same zdarzenia); powrót do jednego zapytania z limitem 2000; dodano filtr `duration > 0` aby liczyć tylko zakończone sesje koszenia (nie zdarzenia startu czy zmiany statusu)

## [1.1.17] - 2026-04-25

### Fixed
- `device.py`: `_populate_stats_from_history` — pobieranie historii zdarzeń było ograniczone do 200 wpisów; przy większej liczbie sesji (np. 215) licznik, łączny czas i powierzchnia były zaniżone; wprowadzono paginację wsteczną po `time_end` pobierającą kolejne batche po 200 aż do wyczerpania historii

## [1.1.16] - 2026-04-24

### Fixed
- `device.py`: `docked` — A1 Pro po pełnym naładowaniu wysyła `charging_status = NOT_CHARGING` zamiast `CHARGING_COMPLETED`; dodano warunek `NOT_CHARGING + battery=100%` → kamera poprawnie wyświetla mapę gdy kosiarka jest zadokowana
- `device.py`: `_set_current_map_data` — brakowało wywołania `_property_changed()` po ustawieniu mapy z chmury; kamera nie dostawała sygnału do odświeżenia widoku
- `device.py`: `_request_cleaning_history` — po wykryciu nowej historii sesji odświeżany jest `CLEANING_COUNT` i statystyki z urządzenia (licznik sesji nie aktualizował się po zakończeniu koszenia)

## [1.1.15] - 2026-04-21

### Fixed
- `device.py`: `_build_map_data_from_zones_json` — gdy `boundary: null` w JSON, wymiary mapy były 1×1 px (obraz niewidoczny); teraz bbox jest obliczany automatycznie z punktów stref + margines 200 jednostek

## [1.1.14] - 2026-04-20

### Changed
- `hacs.json`: zmieniono nazwę integracji z "Dreame Mower A1 Pro" na "Dreame Mower"

## [1.1.13] - 2026-04-20

### Fixed
- `device.py`: Fałszywy błąd "Edge sensor error" wyświetlany przy powrocie kosiarki do ładowarki — A1 Pro wysyła kod 54/57 (EDGE/EDGE_2) jako status powrotu z niską baterią, nie jako rzeczywisty błąd czujnika; dodano do listy wykluczeń (zwraca `NO_ERROR`)

## [1.1.12] - 2026-04-20

### Fixed
- `device.py`: `_build_map_data_from_zones_json` — `"boundary": null` w JSON powodowało crash `'NoneType' object has no attribute 'get'`; zmieniono `map_json.get("boundary", {})` na `map_json.get("boundary") or {}`
- `device.py`: `_build_map_data_from_zones_json` — dodano guard `if not isinstance(zone_data, dict): continue` dla wpisów mowingAreas gdzie `entry[1]` może być `None`

## [1.1.11] - 2026-04-20

### Added
- Wersja integracji widoczna w info urządzenia HA (pole "oprogramowanie") jako `firmware · int. X.Y.Z`

## [1.1.10] - 2026-04-20

### Fixed
- `device.py`: `_build_map_data_from_zones_json` — `map_data.segments` ustawiane jako `None` gdy słownik segmentów był pusty, powodując crash `'NoneType' object has no attribute 'items'` w `lawn_mower.py:609`; zmieniono na zawsze przypisywać dict (nawet pusty)
- `device.py`: `_build_map_data_from_zones_json` — `mowingAreas`, `forbiddenAreas`, `contours` ustawione na `null` w JSON powodowały crash `'NoneType' object has no attribute 'get'`; dodano `or {}` jako fallback przed `.get("value", [])`

## [1.1.9] - 2026-04-20

### Fixed
- `device.py`: A1 Pro mapy historyczne to pliki JSON ze strefami (nie binarny format vacuum) — `get_history_map` (base64 decoder) crashował z `Incorrect padding`; dodano `_build_map_data_from_zones_json` i `_try_use_last_history_map` pobierający plik bezpośrednio przez `get_interim_file_url` + parsujący jako JSON stref; refaktor `_try_build_map_from_batch` używa tej samej metody

## [1.1.8] - 2026-04-20

### Fixed
- `device.py`: `_build_map_from_cloud_data` — obsługa wartości `"null"` w kluczach MAP (urządzenie idle); refaktor na `_try_build_map_from_batch` + `_try_use_last_history_map`
- `device.py`: `_try_use_last_history_map` — gdy MAP batch zwraca null/brak danych (urządzenie śpi), ładuje ostatnią mapę z historii sesji jako statyczną current map; wywoływana też po załadowaniu historii czyszczenia

## [1.1.7] - 2026-04-20

### Fixed
- `device.py`: `_build_map_from_cloud_data` — zmieniono pobieranie chunków MAP.0-MAP.27 na dynamiczne (batche po 32, max 256 kluczy) + szczegółowe logowanie formatu danych; poprzedni zakres był za mały i JSON był obcięty

## [1.1.6] - 2026-04-20

### Fixed
- `map.py`: `_request_i_map` — rozbudowano fallback dreame_cloud: Próba 1 (OBJECT_NAME z get_properties) + Próba 2 (pochodna ścieżka `model/uid/did/0` przez `get_interim_file_url`); dodano szczegółowe logowanie aby ustalić który mechanizm działa dla A1 Pro

## [1.1.5] - 2026-04-20

### Fixed
- `map.py`: `_request_i_map` — gdy akcja `REQUEST_MAP` nie zwraca danych (urządzenia dreame_cloud bez obsługi strumieniowania map, np. A1 Pro), dodano fallback przez `get_properties(OBJECT_NAME)` → `_add_cloud_map_data`; wcześniej fallback dla dreame_cloud był no-op

## [1.1.4] - 2026-04-20

### Fixed
- `device.py`: `_build_map_from_cloud_data` nie wywoływał `_map_data_changed()` po ustawieniu danych — kamera nigdy nie dostawała powiadomienia o nowej mapie (`v=0` w URL)
- `device.py`: mapa z chmury (MAP.0–MAP.27) była pobierana tylko raz przy inicjalizacji — podczas koszenia mapa nie była odświeżana; dodano odświeżanie co 30s gdy kosiarka kosi

## [1.1.3] - 2026-04-20

### Fixed
- Mapa nie była renderowana gdy kosiarka kosi (`status = CLEANING`) a `relocation_status` nie był `LOCATED`/`UNKNOWN` — dodano `running` do warunku wyświetlania mapy w `camera.py`

## [1.1.2] - 2026-04-19

### Fixed
- Encje **Current Map** i **Current Map Data** (kamera) pokazują teraz `idle` zamiast `niedostępny` gdy urządzenie ma obsługę map (`capability.map = True`) ale dane mapy nie zostały jeszcze pobrane w bieżącej sesji

## [1.1.1] - 2026-04-19

### Fixed
- Binary sensory `has_saved_map` i `scheduled_clean` były unavailable — `is_on` odwoływało się do `self.description` zamiast `self.entity_description`
- Encja **Current Map** (kamera) pokazywała "niedostępny" gdy kosiarka jest zadokowana bez połączenia z chmurą — usunięto wymóg `cloud_connected` przy ustawianiu stanu encji

## [1.1.0] - 2026-04-19

### Added
- Binary sensor **Mapa zapisana** (`has_saved_map`) — informuje czy kosiarka ma zapisaną mapę; widoczny tylko gdy urządzenie obsługuje mapy
- Binary sensor **Zaplanowane koszenie** (`scheduled_clean`) — informuje czy aktywne jest zaplanowane koszenie
- Sensor **Całkowity czas pracy** (`total_runtime`) — łączny czas pracy urządzenia w minutach (diagnostic)

### Fixed
- Encja **Current Map** niedostępna gdy kosiarka jest zadokowana — warunek `located` nie uwzględniał stanu `docked`; dodano `or status.docked` w trzech miejscach w `camera.py`

## [1.0.1] - 2026-04-18

### Changed
- Zsynchronizowano zmiany z upstream `nicolasglg/dreame-mova-mower`: sekcja scope of support, zaktualizowana tabela kompatybilności z opisami statusów i informacja o braku wsparcia dla MOVA

## [1.0.0] - 2026-04-18

### Changed
- Fork przejęty przez keysim86 — przemianowany na **ha-dreame-mower** (repo uniwersalne, nie tylko A1 Pro)
- Zaktualizowano README, LICENSE, manifest.json oraz workflow CI/CD
