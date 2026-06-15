# BWT Smart Dos DT Plus – Home Assistant Integration

Eine benutzerdefinierte Home-Assistant-Integration zur lokalen Auslesung eines **BWT Smart Dos DT Plus** über dessen HTTP-API.

Die Integration arbeitet vollständig lokal und benötigt keine Cloud-Verbindung. Die IP-Adresse des Geräts wird bequem über den Home-Assistant-Konfigurationsdialog hinterlegt. Der API-Port wird automatisch auf den Standard-Port **80** gesetzt.

> [!IMPORTANT]
> Dies ist ein inoffizielles Community-Projekt. Es besteht keine Verbindung zu BWT oder dem Home-Assistant-Projekt.

## Funktionen

* Lokale Kommunikation mit dem BWT Smart Dos DT Plus
* Einrichtung über den Home-Assistant-Konfigurationsdialog
* Automatische Prüfung der Verbindung während der Einrichtung
* Standardport 80 wird automatisch verwendet
* Unterschiedliche Abfrageintervalle für Status-, Mess- und Metadaten
* Klartextanzeige der dokumentierten Statusmeldungen
* Fehleranzeige als Home-Assistant-Problem-Binary-Sensor
* Automatische Umrechnung von Wasserwerten in Liter
* Anzeige der Betriebszeit seit dem letzten Neustart als `HH:MM`
* Anzeige der Gesamtbetriebszeit in Tagen
* Wirkstofferkennung über Wirkstoff-ID oder EAN
* Diagnoseinformationen direkt auf der Geräteseite
* Dienst zum Neuladen der Integration
* Unterstützung für HACS

## Voraussetzungen

Vor der Einrichtung müssen folgende Bedingungen erfüllt sein:

1. Der BWT Smart Dos DT Plus ist mit demselben lokalen Netzwerk wie Home Assistant verbunden.
2. Das Gerät wurde in der BWT Best Water App registriert.
3. Die lokale API wurde in den Geräteeinstellungen der BWT Best Water App aktiviert.
4. Die IP-Adresse des Geräts ist bekannt.
5. Home Assistant kann das Gerät über Port 80 erreichen.

Die API ist anschließend beispielsweise unter folgender Adresse erreichbar:

```text
http://192.168.1.100/api/v1/gatt/0201
```

## Installation über HACS

### Repository zu HACS hinzufügen

1. HACS in Home Assistant öffnen.
2. Zu **Integrationen** wechseln.
3. Oben rechts das Drei-Punkte-Menü öffnen.
4. **Benutzerdefinierte Repositories** auswählen.
5. Die Adresse des GitHub-Repositories eintragen:

```text
https://github.com/DEIN-GITHUB-NAME/DEIN-REPOSITORY
```

6. Als Kategorie **Integration** auswählen.
7. Das Repository hinzufügen.
8. Nach **BWT Smart Dos DT Plus** suchen.
9. Die Integration herunterladen.
10. Home Assistant vollständig neu starten.

## Manuelle Installation

Alternativ kann die Integration manuell installiert werden.

Den Ordner

```text
custom_components/bwt_smartdos
```

in das Home-Assistant-Konfigurationsverzeichnis kopieren:

```text
/config/custom_components/bwt_smartdos
```

Die vollständige Verzeichnisstruktur muss anschließend so aussehen:

```text
/config/
└── custom_components/
    └── bwt_smartdos/
        ├── __init__.py
        ├── api.py
        ├── binary_sensor.py
        ├── config_flow.py
        ├── const.py
        ├── coordinator.py
        ├── diagnostics.py
        ├── entity.py
        ├── helpers.py
        ├── manifest.json
        ├── sensor.py
        ├── services.yaml
        ├── strings.json
        └── translations/
            ├── de.json
            └── en.json
```

Danach Home Assistant vollständig neu starten.

## Einrichtung in Home Assistant

Nach dem Neustart:

1. **Einstellungen** öffnen.
2. **Geräte & Dienste** auswählen.
3. **Integration hinzufügen** anklicken.
4. Nach **BWT Smart Dos DT Plus** suchen.
5. Die lokale IP-Adresse des Geräts eingeben.
6. Einrichtung abschließen.

Der Port muss nicht eingegeben werden. Die Integration verwendet automatisch:

```text
Port 80
```

Während der Einrichtung prüft die Integration die Verbindung über folgende API-Endpunkte:

```text
/api/v1/gatt/0201
/api/v1/gatt/0104
```

Die Einrichtung wird nur abgeschlossen, wenn das Gerät erreichbar ist und gültige JSON-Antworten liefert.

## Abfrageintervalle

Die Integration verwendet getrennte Abfrageintervalle, um Statusänderungen schnell zu erkennen und gleichzeitig das Gerät sowie die Home-Assistant-Datenbank nicht unnötig zu belasten.

| Datengruppe                | API-Endpunkte                  |    Intervall |
| -------------------------- | ------------------------------ | -----------: |
| Status und Fehler          | `0201`                         |  10 Sekunden |
| Messwerte                  | `0104`, `0402`, `0503`, `0505` | 120 Sekunden |
| Geräte- und Wirkstoffdaten | `0202`, `0208`, `0401`         | 600 Sekunden |

Da Firmware, Hardware, Status, Betriebszeit und Gesamtbetriebszeit gemeinsam über den Endpunkt `0201` geliefert werden, werden diese Daten technisch ebenfalls mit der 10-Sekunden-Antwort aktualisiert. Dadurch entsteht keine zusätzliche API-Abfrage.

## Sensoren

Auf der Geräteseite werden unter **Sensoren** nur die wichtigsten Betriebswerte angezeigt.

| Sensor       | Beschreibung                                        | Einheit      |
| ------------ | --------------------------------------------------- | ------------ |
| Status       | Aktueller Gerätestatus und aktive Meldungen         | Text         |
| Fehlerstatus | Zeigt an, ob eine Warnung oder ein Fehler aktiv ist | OK / Problem |
| Gesamtwasser | Gesamte aufbereitete Wassermenge                    | l            |
| Restvolumen  | Verbleibende Wirkstoffmenge                         | ml           |
| Restvolumen  | Verbleibende Wirkstoffmenge                         | %            |
| Restvolumen  | Geschätzte verbleibende Nutzungsdauer               | Tage         |

### Statusmeldungen

Die Integration übersetzt die von der API gelieferten Status-IDs in Klartext.

| Status-ID | Klartext                     |
| --------: | ---------------------------- |
|      2001 | Standby                      |
|      2002 | Dosierung aktiv              |
|      7001 | Mineralstoffbehälter niedrig |
|      7002 | Mineralstoffbehälter leer    |
|      7003 | Wirkstoff läuft bald ab      |
|      7004 | Wirkstoff abgelaufen         |
|      7005 | AQA Volume Alarm             |
|      7006 | AQA Watch Alarm              |
|      7007 | AQA MaxFlow Alarm            |
|      8001 | Pumpenfehler                 |
|      8002 | Pumpen Stromfehler           |
|      8003 | Pumpen Steuerungsfehler      |

## Fehlerstatus

Der Fehlerstatus wird als Home-Assistant-Binary-Sensor mit der Geräteklasse `problem` dargestellt.

| Zustand                   | Anzeige |
| ------------------------- | ------- |
| Kein Fehler aktiv         | OK      |
| Warnung oder Fehler aktiv | Problem |

Die konkrete Klartextmeldung wird zusätzlich als Attribut des Fehlerstatus-Sensors gespeichert:

```text
aktive_fehler
```

Beispiel:

```text
aktive_fehler: Mineralstoffbehälter niedrig
```

## Diagnosewerte

Technische Geräteinformationen und weniger wichtige Metadaten werden unter **Diagnose** angezeigt.

| Diagnosewert             | API-Feld                        |
| ------------------------ | ------------------------------- |
| WLAN Signal              | `0104.rssiAvg` oder `0104.rssi` |
| Betriebszeit seit Reboot | `0201.uptime`                   |
| Gesamtbetriebszeit       | `0201.operatingTime`            |
| Dosierte Wirkstoffmenge  | `0505.dosedMineral`             |
| Firmware                 | `0201.fwRev`                    |
| Hardware                 | `0201.hwRev`                    |
| Produktcode              | `0201.productCode`              |
| MAC-Adresse              | `0104.mac`                      |
| Inbetriebnahmedatum      | `0201.commDate`                 |
| Pouchvolumen             | `0401.*.totCap`                 |
| Bestellnummer            | `0401.*.orderNr`                |
| Chargennummer            | `0401.*.batchNr`                |
| Wirkstofftyp             | `0401.*.id` oder `0401.*.ean`   |
| Wirkstoff Ablaufdatum    | `0401.*.expDate`                |

### Betriebszeit seit Reboot

Die Betriebszeit seit dem letzten Neustart wird als verstrichene Zeit im Format `HH:MM` angezeigt.

Beispiele:

```text
00:43
12:05
27:15
```

Die Stunden können dabei größer als 23 werden. Die Anzeige wird nicht täglich auf null zurückgesetzt.

### Gesamtbetriebszeit

Die Gesamtbetriebszeit wird in Tagen angezeigt.

Beispiel:

```text
52,11 d
```

## Wirkstofftypen

Wenn das Gerät eine gültige Wirkstoff-ID liefert, wird diese direkt ausgewertet.

| ID | Wirkstofftyp |
| -: | ------------ |
|  1 | L1/LE        |
|  2 | L2/L3        |
|  3 | L4           |
|  4 | CU2          |
|  5 | Spüllösung   |

Einige Firmware-Versionen liefern bei `id` den Wert `0`. In diesem Fall versucht die Integration, den Wirkstofftyp über die EAN zu bestimmen.

Aktuell hinterlegter EAN-Fallback:

|           EAN | Wirkstofftyp |
| ------------: | ------------ |
| 9022000010354 | L1/LE        |

Weitere EAN-Zuordnungen können zukünftig ergänzt werden.

## Verwendete API-Endpunkte

| UUID   | Inhalt                                                     |
| ------ | ---------------------------------------------------------- |
| `0104` | WLAN-Informationen und MAC-Adresse                         |
| `0201` | Firmware, Hardware, Produktcode, Betriebszeiten und Status |
| `0202` | Gerätekonfiguration und AQA-Einstellungen                  |
| `0208` | Gerätezeit und Zeitzone                                    |
| `0401` | Pouch-, Wirkstoff- und Ablaufdaten                         |
| `0402` | Verbleibende Wirkstoffmenge                                |
| `0503` | Aufbereitete Wassermenge                                   |
| `0505` | Dosierte Wirkstoffmenge                                    |

## Einheiten und Berechnungen

### Gesamtwasser

Die API liefert die Wassermenge über:

```text
0503.flow.*.totFlow
```

Die Werte werden von der Integration über alle vorhandenen Kanäle summiert.

Da die API die Menge in Millilitern liefert, erfolgt anschließend die Umrechnung in Liter:

```text
Liter = Milliliter / 1000
```

### Dosierte Wirkstoffmenge

Die dosierte Wirkstoffmenge wird über folgendes Feld ausgelesen:

```text
0505.dosedMineral
```

Die Anzeige erfolgt in Millilitern.

### Fehlende API-Werte

Einige Geräte oder Firmware-Versionen liefern für bestimmte Werte `null`, `0` oder einen leeren Text.

In diesem Fall wird angezeigt:

```text
Nicht von API geliefert
```

Dies betrifft möglicherweise:

* Bestellnummer
* Chargennummer
* Wirkstoff-ID
* weitere Metadaten

Die Integration kann nur Daten anzeigen, die das Gerät tatsächlich über seine lokale API bereitstellt.

## Dienst zum Neuladen

Die Integration stellt folgenden Home-Assistant-Dienst bereit:

```text
bwt_smartdos.reload
```

Ohne Parameter werden alle eingerichteten BWT-Smart-Dos-Instanzen neu geladen.

Optional kann eine bestimmte Konfiguration über ihre Entry-ID neu geladen werden:

```yaml
action: bwt_smartdos.reload
data:
  entry_id: 0123456789abcdef
```

Beim Neuladen werden auch die Geräte- und Wirkstoffdaten erneut abgefragt.

## Aktualisierung

Bei einem Update über HACS:

1. Neue Version in GitHub veröffentlichen.
2. HACS in Home Assistant öffnen.
3. Die Integration **BWT Smart Dos DT Plus** auswählen.
4. **Neu herunterladen** oder **Aktualisieren** auswählen.
5. Home Assistant vollständig neu starten.
6. Unter **Einstellungen → Geräte & Dienste** kontrollieren, ob die neue Version geladen wurde.

Die aktuelle Versionsnummer steht in:

```text
custom_components/bwt_smartdos/manifest.json
```

## Fehlerbehebung

### Integration erscheint nicht in Home Assistant

Prüfen:

* Wurde der Ordner korrekt nach `/config/custom_components/bwt_smartdos` kopiert?
* Ist die Datei `manifest.json` vorhanden?
* Wurde Home Assistant vollständig neu gestartet?
* Enthält der Ordner möglicherweise noch eine zusätzliche Unterebene?

Falsch:

```text
/config/custom_components/bwt_smartdos/bwt_smartdos/manifest.json
```

Richtig:

```text
/config/custom_components/bwt_smartdos/manifest.json
```

### Konfigurationsfluss kann nicht geladen werden

Home-Assistant-Protokoll unter folgendem Menü prüfen:

```text
Einstellungen → System → Protokolle
```

Außerdem sicherstellen, dass:

* `config_flow.py` vorhanden ist
* in `manifest.json` `"config_flow": true` eingetragen ist
* der Domain-Name überall `bwt_smartdos` lautet
* Home Assistant nach dem Update vollständig neu gestartet wurde

### Verbindung zum Gerät nicht möglich

Folgende Adresse im Browser testen:

```text
http://GERÄTE-IP/api/v1/gatt/0201
```

Wenn keine JSON-Antwort erscheint:

* API in der BWT-App aktivieren
* IP-Adresse kontrollieren
* Netzwerkverbindung prüfen
* VLAN- oder Firewall-Regeln prüfen
* sicherstellen, dass Home Assistant und das Gerät miteinander kommunizieren dürfen

### Alte Entitäten werden weiterhin angezeigt

Nach größeren Updates können alte Einträge kurzzeitig in der Entity Registry vorhanden sein.

Vorgehen:

1. Home Assistant vollständig neu starten.
2. Integration neu laden.
3. Browseransicht aktualisieren.
4. Falls nötig unter **Einstellungen → Geräte & Dienste → Entitäten** nach alten Einträgen suchen.

Die Integration entfernt bekannte veraltete Entity-Einträge bei der Migration automatisch.

### Wirkstofftyp wird nicht angezeigt

Den Endpunkt prüfen:

```text
http://GERÄTE-IP/api/v1/gatt/0401
```

Relevant sind:

```json
{
  "id": 0,
  "ean": 9022000010354
}
```

Wenn `id` zwischen 1 und 5 liegt, wird die ID verwendet.

Wenn `id` den Wert `0` hat, wird versucht, die EAN auszuwerten. Ist die EAN nicht in der Integration hinterlegt, wird `Nicht von API geliefert` angezeigt.

## Diagnose herunterladen

Home Assistant kann Diagnoseinformationen der Integration bereitstellen.

Dazu:

1. **Einstellungen → Geräte & Dienste** öffnen.
2. Die BWT-Smart-Dos-Integration auswählen.
3. Drei-Punkte-Menü öffnen.
4. **Diagnose herunterladen** auswählen.

Sensible Daten wie IP-Adresse, MAC-Adresse, WLAN-Name oder Geräte-ID werden in den Diagnoseinformationen anonymisiert.

## Datenschutz

Die Integration kommuniziert ausschließlich lokal mit dem BWT Smart Dos DT Plus.

Es werden durch diese Integration keine Gerätedaten an externe Server übertragen.

Die Kommunikation erfolgt unverschlüsselt über HTTP im lokalen Netzwerk:

```text
Port 80
```

Das Gerät sollte daher nicht direkt aus dem Internet erreichbar gemacht werden.

## Datenbank und Leistung

Die Integration verwendet für die wichtigsten Messwerte Home-Assistant-kompatible Zustandsklassen.

Die Polling-Intervalle wurden so gewählt, dass:

* Statusänderungen schnell erkannt werden
* Messwerte regelmäßig aktualisiert werden
* Metadaten das Gerät nicht unnötig häufig belasten

Textsensoren und Diagnosewerte können trotzdem in der Home-Assistant-Datenbank gespeichert werden. Die tatsächliche Datenbankgröße hängt zusätzlich von den Recorder-Einstellungen in Home Assistant ab.

## Bekannte Einschränkungen

* Nicht alle Firmware-Versionen liefern alle dokumentierten API-Werte.
* Bestellnummer und Chargennummer können von der API als `0` geliefert werden.
* Der Wirkstofftyp kann bei manchen Geräten nur über die EAN bestimmt werden.
* Die API verwendet unverschlüsseltes HTTP.
* Die Integration wurde ausschließlich mit den bekannten Antworten eines BWT Smart Dos DT Plus entwickelt.
* Andere Geräte der BWT-Smart-Dos-Reihe können abweichende JSON-Strukturen liefern.

## Unterstützte Home-Assistant-Version

Empfohlen wird eine aktuelle Home-Assistant-Version.

Die Integration wurde als moderne Config-Flow-Integration mit `DataUpdateCoordinator` umgesetzt.

## Beiträge

Fehlerberichte und Verbesserungen sind willkommen.

Bitte bei einem Fehlerbericht möglichst folgende Informationen angeben:

* Home-Assistant-Version
* Version der Integration
* Firmware-Version des BWT Smart Dos
* relevante Fehlermeldung aus dem Home-Assistant-Protokoll
* anonymisierte Diagnoseinformationen
* anonymisierte JSON-Antwort des betroffenen API-Endpunkts

Bitte keine privaten Daten wie IP-Adresse, MAC-Adresse oder Geräte-ID veröffentlichen.

## Haftungsausschluss

Die Nutzung erfolgt auf eigene Verantwortung.

Die Entwickler übernehmen keine Haftung für:

* fehlerhafte Messwerte
* Ausfälle des Geräts
* Schäden an Home Assistant oder dem BWT-Gerät
* Änderungen der BWT-API
* inkompatible Firmware-Updates

Diese Integration greift ausschließlich lesend auf die dokumentierten API-Endpunkte zu.

