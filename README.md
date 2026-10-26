# Eduvize – Moudrost dne

Samostatný modul Eduvize. Jediným zdrojem nových citátů je **ZenQuotes**, jedinou překladovou službou **DeepL**.

## Bezpečnost a publikování
- GitHub Actions načítá dávku citátů z `https://zenquotes.io/api/quotes`.
- Nové položky překládá do CS a SK přes DeepL API na serveru GitHub Actions.
- Ukládá je pouze do `data/pending.json`; **nepublikuje je automaticky**.
- Správce zkontroluje obsah i překlady a vhodné záznamy přesune do `data/approved.json` (pole `id,en,cs,sk,author,source`).
- Výstupní stránka používá výhradně schválené položky. Při výpadku API zůstávají schválená data dostupná.

## Nastavení
1. V repozitáři otevřete **Settings → Secrets and variables → Actions → New repository secret**.
2. Vložte **DEEPL_API_KEY**. Klíč nikdy nevkládejte do HTML ani do veřejného repozitáře.
3. V **Settings → Actions → General → Workflow permissions** povolte **Read and write permissions**.
4. Spusťte **Actions → Fetch and translate ZenQuotes → Run workflow**.
5. Zkontrolujte `data/pending.json` a vhodné položky přesuňte do `data/approved.json`.

ZenQuotes bez placeného klíče negarantuje filtrování podle kategorií a vyžaduje uvedení zdroje. Provozní limity a podmínky komerčního použití ověřte u poskytovatele. DeepL API klíč je vyžadován. GitHub Pages neprovádí volání překladové služby.
