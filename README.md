# Eduvize – Moudrost dne

Samostatný modul citátů pro školní informační obrazovky Eduvize.

## Aktivní databáze
`data/approved.json` obsahuje kurátorované výroky osobností s odkazy na webové zdroje. Dne 26. 10. 2026 bylo odstraněno 65 starších záznamů: 24 testovacích lidových přísloví a 41 záznamů původně čerpaných z projektů Wikimedia. Zbylo 429 záznamů.

## Pravidla konzistence
- Každý záznam: identifikátor, text, jazyk, téma, autor, zdroj a pokud možno přímý odkaz.
- Původní zdroj má přednost před agregátorem citátů; webový odkaz sám o sobě neprokazuje správné autorství ani oprávnění k použití.
- Pracovní kandidáti v `data/candidates_*.json` a dalších rešeršních souborech nejsou automaticky schválené citáty.
- Neověřené překlady, parafráze a licenční otázky vyžadují další revizi před veřejným použitím.
- Při doplňování odstraňovat duplicity podle autora a normalizovaného textu.
- Jeden citát může mít více tematických kategorií, nemá být uložen vícekrát.

## Import
Starší import z Wikizdrojů je vypnutý v `.github/workflows/wikisource.yml`. Skript `scripts/import_wikisource.py` zůstává jen jako historický zdrojový kód a nemá se spouštět pro produkční databázi.

## Konfigurace
`config.html`: jazyk, téma, interval. Nastavení se ukládá lokálně v prohlížeči.
