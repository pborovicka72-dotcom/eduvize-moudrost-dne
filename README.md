# Eduvize – Moudrost dne

Bezobslužná aplikace pro školní informační obrazovky, v češtině a slovenštině. Překlad ani ruční schvalování není vyžadováno.

## Databáze
`data/approved.json` obsahuje tradiční lidová přísloví. Automatický import z českých Wikizdrojů je v `scripts/import_wikisource.py`; spouští jej `.github/workflows/wikisource.yml` jednou týdně nebo ručně.

## Přísný licenční filtr
Import přijme pouze samostatný krátký text na stránce s explicitní rozpoznanou licenční šablonou: PD-traditional, PD-old, PD-70, CC0, CC-BY-4.0 nebo CC-BY-SA-4.0. Uloží název díla, odkaz a licenci. Bez explicitního údaje nepřebírá nic. Licenční údaj může být na Wikizdrojích uveden v jiných šablonách nebo na nadřazené stránce; takové záznamy se zatím přeskočí. **Nejde o úplný import všech volných děl** a samotné rozpoznání šablony není právní zárukou.

Záměrně se neimportují dlouhá díla ani náhodné věty vytržené z kontextu. Automatická extrakce je omezená na jednořádková samostatná díla. Pro CC BY / BY-SA musí být dodržena atribuce a příslušné licenční podmínky; samotný odkaz na zdroj nemusí splnit všechny požadavky.

## Konfigurace
`config.html`: jazyk, téma, interval. Nastavení se ukládá lokálně v prohlížeči. Pro GitHub Actions povolte v Settings → Actions → General právo zápisu do repozitáře.
