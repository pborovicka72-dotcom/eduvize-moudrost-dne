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
`config.html`: věková skupina, 1–3 citáty za den, střídání autorů, témata,
osobnosti, zdrojový odkaz a režim web/NSP/kiosek. Citáty se mění v časových
blocích podle místního času zařízení.

Místní koncepty a výběr segmentu jsou oddělené podle školy a profilu.
Staré nespecifikované lokální nastavení se načítá pouze do anonymního
neprofilového konceptu, nikoli do profilu školy. Původní data se nemažou.
Při změně identity nelze rozepsané nastavení zapsat pod jiný profil bez
načtení jeho konfigurace nebo obnovení stránky.

Společné tlačítko Uložit do Eduvize ukládá konfiguraci přes profilové API
s kontrolou revize. Adaptér čeká na dokončení načítání a před použitím
konfigurace ověřuje schéma, hodnoty, katalog a geometrii.
Klientská validace nenahrazuje oprávnění a validaci na backendu.

Veřejný obsah se řídí URL a výchozími hodnotami, nikdy místním konceptem.
Prázdný výběr témat či autorů znamená všechny, i v prohlížeči s cizím konceptem.
Odkazy stále představují současný přechodný formát; nejsou novým publikovaným
výstupním kontraktem. Sdílené assety HTML se načítají ze stejného originu.

## Příprava testu

`node --test tests/*.test.mjs` ověřuje izolaci konceptů, nezávislost obsahu
na localStorage, explicitní filtry URL a validaci konfigurace. CI kontroly
běží v PR; sloučení do main spouští existující izolované testovací nasazení.
Produkční nasazení má samostatné schválení vlastníkem.

Před přijetím na testu ověřit cloudové uložení/obnovu dvěma školami a profily,
záměnu identity během editace, náhled a výstup web/NSP/kiosek a obě orientace.
Při chybě načtení katalogu se nesmí hlásit úspěšné cloudové obnovení.

## Čeká na společné rozhraní

- Serverový registr, neprůhledné ID, jediný generátor a veřejný resolver.
- Oddělení konceptu od atomické publikace a stabilní veřejné adresy.
- Kontext stylu, licence a aktualizačních plánů určený resolverem namísto
  relace, localStorage či záložního profilu ve sdílených komponentách.
- Centrální konfigurace endpointů a úplná serverová validace schématu wisdom.
- Důkaz nezávislosti na Renderu: blokace na klientu i serveru, prázdná cache
  a restart služeb. Samotný přepis endpointů při sestavení není tento důkaz.

Historické vývojové odkazy není nutné zachovávat (rozhodnutí 6. 11. 2026);
stabilita adres je závazná od prvního stabilního vydání nového kontraktu.
