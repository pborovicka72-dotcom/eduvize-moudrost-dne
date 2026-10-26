# Eduvize – Moudrost dne

Samostatná aplikace Eduvize. **Zdroje: české a slovenské Wikicitáty (Wikiquote). Bez DeepL, ZenQuotes a jiného překladového API.**

## Provoz
- `index.html` zobrazuje jen ručně schválené záznamy z `data/approved.json`.
- `config.html` nastavuje jazyk (čeština nebo slovenština), kategorii a interval přepínání, lokálně v prohlížeči.
- GitHub Actions `Import Wikicitáty for review` načítá z kategorií definovaných v `data/categories.json` kandidáty do `data/pending.json`.
- Import nepřidává nic přímo na veřejnou nástěnku. **Každý citát musí správce zkontrolovat** (vhodnost, význam, autorství, licence) a ručně převést do `data/approved.json`.
- Formát schváleného záznamu: `id,text,language,topic,author,source,source_url`. Zachovejte URL původu a informace o licenci/atribuci.
- Kategorie Wikicitátů třídí stránky, nikoli jednotlivé výroky; import používá jednoduchou extrakci odrážek a výsledky vyžadují kontrolu.
- Seznam kategorií je výchozí návrh: názvy a dostupnost na konkrétní wiki se mohou lišit. Před ostrým provozem je ověřte.

## Práva
Obsah Wikicitátů může mít licenční a autorskoprávní omezení. Před publikací ověřte licenci konkrétního obsahu, požadované uvedení autorů, odkazu a podmínky dalšího užití. Automatický import není právní kontrola.

## GitHub Actions
V Settings → Actions → General nastavte Workflow permissions → Read and write permissions. Poté lze ručně spustit import přes Actions. Žádný API klíč není potřeba.
