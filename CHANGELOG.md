# Changelog

## [Unreleased]

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
