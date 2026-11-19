# Polityka prywatności — StreamRemaster

*Ostatnia aktualizacja: 19 listopada 2026 r.*

*[English](PRIVACY.md) · [Español](PRIVACY.es.md) · [Deutsch](PRIVACY.de.md) · [Français](PRIVACY.fr.md) · [Italiano](PRIVACY.it.md) · [Nederlands](PRIVACY.nl.md) · [Polski](PRIVACY.pl.md) · [Português](PRIVACY.pt.md) · [Русский](PRIVACY.ru.md) · [Українська](PRIVACY.uk.md) · [简体中文](PRIVACY.zh-CN.md) · [日本語](PRIVACY.ja.md) · [한국어](PRIVACY.ko.md) · [ไทย](PRIVACY.th.md) · [हिन्दी](PRIVACY.hi.md) · [Català](PRIVACY.ca.md) · [Galego](PRIVACY.gl.md) · [Euskara](PRIVACY.eu.md)*

## 1. Administrator danych

Wydawcą rozszerzenia przeglądarki StreamRemaster, wcześniej noszącego nazwę Stream Transcription („Rozszerzenie”), publikowanego w serwisie addons.mozilla.org oraz pod adresem https://github.com/javimentallab/StreamRemaster, jest Javier Comyn Pérez, adres: calle Olivos, número 36, 28670 Villaviciosa de Odón, Madrid, España („Dostawca”), działający pod nazwą dewelopera javimentallab. Dostawca jest administratorem danych osobowych, o których mowa w niniejszej polityce, która podlega rozporządzeniu (UE) 2016/679 – ogólnemu rozporządzeniu o ochronie danych („RODO”), oraz hiszpańskiej ustawie organicznej 3/2018 z dnia 5 grudnia o ochronie danych osobowych i gwarancji praw cyfrowych (Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales). Użytkownik Rozszerzenia („Użytkownik”) może kontaktować się z Dostawcą pod adresem jotacomyn@gmail.com.

## 2. Brak przetwarzania danych osobowych w Rozszerzeniu

Rozszerzenie nie zbiera ani nie przetwarza żadnych danych osobowych Użytkownika w imieniu Dostawcy. Rozszerzenie nie posiada kont użytkowników, reklam, narzędzi analitycznych ani systemów raportowania awarii i nie komunikuje się z żadnym serwerem Dostawcy; nie zawiera i nie będzie zawierać żadnego z tych elementów. Do Dostawcy nie docierają żadne dane Użytkownika ani dźwięk, ani obrazy przetwarzane przez Rozszerzenie. Jedynymi danymi osobowymi, które Dostawca może przetwarzać, są dane przekazane mu przez Użytkownika z własnej inicjatywy w związku z kontaktem z Dostawcą, zgodnie z punktem 7.

## 3. Działanie Rozszerzenia

**3.1. Napisy z wykorzystaniem serwera Użytkownika.** Gdy Użytkownik włącza napisy w trybie serwera, Rozszerzenie przesyła dźwięk z karty na adres serwera wprowadzony w Rozszerzeniu przez samego Użytkownika, zazwyczaj serwer WhisperLive zainstalowany na komputerze Użytkownika lub w jego sieci lokalnej, i odbiera od niego napisy. Serwer ten jest instalowany i kontrolowany przez Użytkownika, który ponosi wyłączną odpowiedzialność za jego konfigurację i bezpieczeństwo; Dostawca nie ma dostępu ani do tego serwera, ani do dźwięku.

**3.2. Napisy na komputerze Użytkownika.** Gdy Użytkownik wybiera transkrypcję na komputerze, dźwięk jest przetwarzany w przeglądarce, na karcie graficznej Użytkownika, i nie opuszcza komputera.

**3.3. Płynne wideo.** Funkcja płynnego wideo przetwarza obrazy wideo na stronie w przeglądarce, na karcie graficznej Użytkownika. Obrazy nie opuszczają komputera i nie są przechowywane.

## 4. Komunikacja z podmiotami trzecimi

Rozszerzenie łączy się z witrynami innymi niż serwer Użytkownika wyłącznie na wyraźne żądanie Użytkownika i wyłącznie w następujących przypadkach:

- **GitHub (api.github.com).** Wyłącznie gdy Użytkownik naciśnie „Sprawdź aktualizacje”, Rozszerzenie odpytuje GitHub o numer najnowszej opublikowanej wersji. Zapytanie nie zawiera żadnych danych dotyczących Użytkownika ani korzystania przez niego z Rozszerzenia.
- **Hugging Face (huggingface.co).** Wyłącznie gdy Użytkownik pobiera model transkrypcji w celu korzystania z niego na komputerze, Rozszerzenie pobiera go z Hugging Face.
- **Adresy wprowadzone przez Użytkownika.** Gdy Użytkownik dodaje model płynnego wideo, podając jego adres, Rozszerzenie pobiera go z tego adresu.

Jak w przypadku każdego połączenia przez internet, witryna, z którą łączy się Rozszerzenie, otrzymuje adres IP Użytkownika i identyfikator jego przeglądarki. Każda z tych witryn przetwarza te dane jako administrator, zgodnie z własną polityką prywatności, za którą Dostawca nie odpowiada.

## 5. Uprawnienia

- **Przechowywanie danych (storage):** przechowywanie ustawień Rozszerzenia w przeglądarce.
- **Przechwytywanie karty (tabCapture i offscreen), wyłącznie w przeglądarkach opartych na Chromium:** uzyskanie dźwięku z karty, w której Użytkownik włącza napisy, wyłącznie po naciśnięciu przez Użytkownika przycisku Rozszerzenia na tej karcie.
- **Aktywna karta i wykonywanie skryptów (activeTab i scripting), wyłącznie w przeglądarkach opartych na Chromium:** wyświetlanie napisów i stosowanie płynnego wideo na karcie, na której Użytkownik nacisnął przycisk Rozszerzenia.
- **Dostęp do witryn internetowych (<all_urls>):** w przeglądarce Firefox odczytywanie dźwięku i obrazu wideo ze strony na potrzeby napisów i płynnego wideo. W przeglądarkach opartych na Chromium jest to uprawnienie opcjonalne, o które Rozszerzenie prosi wyłącznie wtedy, gdy Użytkownik zaznaczy pole automatycznie włączające płynne wideo w dowolnej witrynie internetowej.

## 6. Dane przechowywane w przeglądarce

Rozszerzenie przechowuje w pamięci przeglądarki Użytkownika swoje ustawienia (adres serwera, model, języki, rozmiar i położenie napisów oraz opcje płynnego wideo), modele płynnego wideo dodane przez Użytkownika oraz modele transkrypcji pobrane przez Użytkownika w celu korzystania z nich na komputerze. Dane te pozostają w przeglądarce Użytkownika, nie są przesyłane do Dostawcy i są usuwane po odinstalowaniu Rozszerzenia; modele można również usunąć w ustawieniach Rozszerzenia. Jeżeli Użytkownik włączy opcję zapisywania napisów, po ich zatrzymaniu na komputer Użytkownika pobierany jest plik `.srt`, który pozostaje do dyspozycji Użytkownika.

## 7. Dane z komunikacji Użytkownika

Gdy Użytkownik kontaktuje się z Dostawcą za pośrednictwem poczty elektronicznej, Dostawca przetwarza adres e-mail Użytkownika, jego imię i nazwisko, jeżeli zostały podane, oraz treść wiadomości. Gdy Użytkownik tworzy zgłoszenie w serwisie GitHub, zgłoszenie to jest publiczne i podlega warunkom oraz polityce prywatności GitHub.

Zgodnie z art. 13 RODO podaje się następujące informacje:

- **Cel:** rozpatrzenie zapytania, zgłoszenia lub wniosku Użytkownika.
- **Podstawa prawna:** zgoda Użytkownika wyrażona poprzez skontaktowanie się z Dostawcą (art. 6 ust. 1 lit. a RODO), a w przypadku wykonywania praw, o których mowa w punkcie 8, wypełnienie obowiązku prawnego ciążącego na Dostawcy (art. 6 ust. 1 lit. c RODO).
- **Okres przechowywania:** czas niezbędny do rozpatrzenia korespondencji, a następnie okres przedawnienia roszczeń, które mogą z niej wyniknąć. Po upływie tego okresu dane są usuwane.
- **Odbiorcy:** dane nie są ujawniane podmiotom trzecim, z wyjątkiem przypadków wymaganych przez prawo. Usługę poczty elektronicznej Dostawcy świadczy Google jako usługodawca.

## 8. Prawa Użytkownika

Użytkownik może wykonywać prawa dostępu, sprostowania, usunięcia, ograniczenia przetwarzania, sprzeciwu i przenoszenia danych, na podstawie art. 15–22 RODO, a także w dowolnym momencie wycofać zgodę, bez wpływu na zgodność z prawem przetwarzania, którego dokonano przed jej wycofaniem, kontaktując się z Dostawcą pod adresem jotacomyn@gmail.com. Użytkownik może również wnieść skargę do Agencia Española de Protección de Datos (Hiszpańskiej Agencji Ochrony Danych, www.aepd.es).

## 9. Zmiany

Dostawca może zmieniać niniejszą politykę; data ostatniej aktualizacji jest podana na początku niniejszego dokumentu.

## 10. Kontakt

Zapytania dotyczące niniejszej polityki można kierować do Dostawcy pod adresem jotacomyn@gmail.com lub poprzez utworzenie zgłoszenia na stronie https://github.com/javimentallab/StreamRemaster/issues.
