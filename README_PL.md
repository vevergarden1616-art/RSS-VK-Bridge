# VK → RSS (GitHub Actions) – *gotowiec*

To repo (szablon) buduje **RSS** z profilu/strony **VK (VKontakte)** i hostuje go na **GitHub Pages**. Działa z **Feed Reader Botem** (Telegram) – dodajesz zwykły link do RSS.

---

## 0) Co to robi
- Pobiera posty z VK przez **oficjalne VK API** (`wall.get`, v=5.199).
- Wymaga **Access Tokena VK** (bezpiecznie w **GitHub Secrets**).
- Buduje RSS do `docs/feed.xml` i publikuje przez **GitHub Pages**.
- Odświeża się automatycznie przez **GitHub Actions** (CRON, domyślnie co godzinę).

> **Uwaga**: Działasz w ramach ToS VK. Token traktuj jak hasło. Najlepiej użyj oddzielnego konta/aplikacji.

---

## 1) Załóż repo na GitHubie
1. Wejdź na **github.com** → zaloguj się / załóż konto.
2. Kliknij **+** (prawy górny róg) → **New repository**.
3. Nazwij np. `vk-rss` (może być prywatne – *Private*).
4. Kliknij **Create repository**.

---

## 2) Wgraj pliki z tego ZIP-a
- W repo → **Add file** → **Upload files** → przeciągnij *całą zawartość* rozpakowanego ZIP-a → **Commit changes**.

Struktura:
```
vk-rss/
├─ .github/workflows/build.yml
├─ docs/feed.xml           # placeholder RSS (zastąpi się po pierwszym buildzie)
├─ build_vk_feed.py
├─ requirements.txt
├─ .gitignore
└─ README_PL.md            # ten plik
```

---

## 3) Włącz GitHub Pages
1. Repo → **Settings** → **Pages**.
2. **Source**: *Deploy from a branch*.
3. **Branch**: `main` (albo `master`) oraz **Folder**: `/docs` → **Save**.
4. Twój RSS będzie pod adresem:  
   `https://<twoj-login>.github.io/<nazwa-repo>/feed.xml`

---

## 4) Dodaj **GitHub Secrets** (VK Access Token)
1. Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
2. Dodaj:
   - **Name:** `VK_TOKEN` → **Secret:** *twój token VK*

### Jak zdobyć **VK Access Token** najprościej
- Załóż **aplikację** w VK (typ *Standalone*). W panelu deweloperskim VK zobaczysz **App ID** (client_id).
- Wejdź w przeglądarce na URL autoryzacji (wstaw swój `client_id`):  
  `https://oauth.vk.com/authorize?client_id=CLIENT_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=wall,offline&response_type=token&v=5.199`  
  Zaloguj się, **Zezwól**. W adresie (po `#`) pojawi się `access_token=...` – skopiuj to i wklej jako **`VK_TOKEN`** w Secrets.

> **Uwaga:** Token `offline` nie wygasa szybko. Chroń go w Secrets (nie w kodzie!).

---

## 5) Ustaw profil/stronę VK do pobierania
Domyślnie skrypt czyta zmienne środowiskowe z workflow:
- `VK_DOMAIN` – **screen name** (np. `durov`, `meduza`), *albo*
- `VK_OWNER_ID` – **ID** właściciela ściany (user: dodatni, grupa: **ujemny** ID, np. `-1` to grupa o ID 1).

Wystarczy jedno z nich. W pliku `.github/workflows/build.yml` podmień `VK_DOMAIN` na swój (np. `twoj_nick_vk`).

---

## 6) Odpal pierwszy build
1. Repo → **Actions** → workflow **build-vk-feed** → **Run workflow**.
2. Po zielonym buildzie wejdź w:  
   `https://<twoj-login>.github.io/<nazwa-repo>/feed.xml` – powinny być realne wpisy.

---

## 7) Dodaj do Feed Reader Bota (Telegram)
W rozmowie z botem wpisz:
```
/add https://<twoj-login>.github.io/<nazwa-repo>/feed.xml
```
Gotowe – bot zacznie wysyłać nowe wpisy.

---

## 8) Zmiany i warianty
- **Częstotliwość**: zmień CRON w `.github/workflows/build.yml` (np. co 30 min).
- **Wiele profili**: sklonuj workflow i zapisuj do **innego** pliku, np. `docs/durov.xml` (patrz komentarz w workflow).
- **Załączniki**: skrypt generuje linki do zdjęć/wideo/dokumentów, wyciąga największą fotkę itp.

---

## 9) Rozwiązywanie problemów
- **Błąd autoryzacji**: token wygasł/odwołany – wygeneruj nowy i podmień `VK_TOKEN`.
- **Pusty feed**: profil ma brak postów publicznych lub złe ID/DOMAIN. Upewnij się, że `VK_DOMAIN`/`VK_OWNER_ID` jest poprawne.
- **Rate limits VK**: nie ustawiaj bardzo częstego CRON-a (np. co 1–5 min) – zacznij od 30–60 min.

---

**Bezpieczeństwo**: Token to **hasło** – nigdy nie wklejaj go do kodu ani do Issues. Trzymaj w **GitHub Secrets**.
