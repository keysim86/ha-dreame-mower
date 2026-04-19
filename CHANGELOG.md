# Changelog

## [Unreleased]

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
