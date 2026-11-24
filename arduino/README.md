# Manueller Arduino-Test für die Sortierklappen

Der neue, direkt in der Arduino IDE öffnende Sketch liegt in
`sorter_test/sorter_test.ino`. Die beiden älteren Dateien im Ordner `arduino/`
bleiben als unveränderte Versuchsstände erhalten. Dieser Test hat **keine
Verbindung zur Kamera oder KI-Entscheidung**; die Buttons betätigen die Klappen
unmittelbar.

## Zwei Motoren an Flap 2

Die Beschreibung gilt für die vorhandenen **5-V-28BYJ-48-Motoren mit
ULN2003-Treiberplatinen**. Jeder Motor braucht eine eigene Platine und steckt
mit seinem unveränderten fünfpoligen Motorstecker in **seiner** Platine. Nur
die vier **IN-Eingänge** der beiden Flap-2-Platinen teilen sich Arduino-Pins:

| Arduino | Flap 2: bisherige Platine | Flap 2: neue Platine |
| --- | --- | --- |
| D4 | IN1 | IN4 |
| D5 | IN2 | IN3 |
| D6 | IN3 | IN2 |
| D7 | IN4 | IN1 |

Flap 1 bleibt IN1→D8, IN2→D9, IN3→D10, IN4→D11. Alle drei Treiberplatinen
bekommen +5 V und GND aus einem **externen, ausreichend belastbaren
5-V-Netzteil**; das Netzteil-GND wird zusätzlich mit Arduino-GND verbunden.
Das vorhandene 2-A-Netzteil ist ein sinnvoller Ausgangspunkt, sofern seine
5 V unter Last stabil bleiben. Die Motoren nicht aus Arduino-I/O-Pins oder
dem USB-Anschluss speisen. Die Ausgänge der beiden Treiberplatinen **nicht**
zusammenschalten und den fünfpoligen Motorstecker **nicht umdrehen**.

Die vertauschte IN-Reihenfolge kehrt die elektrische Schrittrichtung des
zweiten Motors um. Ob die Flap dadurch tatsächlich von beiden Seiten in
dieselbe Richtung bewegt wird, hängt von der Montage ab: **beide Wellen
zuerst ohne mechanische Kopplung mit kleinen Schritten testen**. Falls die
Richtung falsch ist, den neuen Treiber IN1→D4, IN2→D5, IN3→D6, IN4→D7
anschließen. Bei gemeinsam genutzten Pins sind die beiden Flap-2-Motoren
nicht unabhängig korrigierbar. Verspannung, ungleiche Getriebestellung oder
ein schwaches Netzteil können beide Motoren gegeneinander arbeiten lassen.
Flap leichtgängig ausrichten und unter Last beobachten; ein stärkerer,
passender Motor samt Treiber kann die bessere mechanische Lösung sein.

## Sketch und UI starten

Die VS-Code-Erweiterung **Arduino Community Edition**
(`vscode-arduino.vscode-arduino-community`) ist für dieses Projekt
vorbereitet: `.vscode/settings.json` aktiviert Arduino CLI und die lokale
`.vscode/arduino.json` wählt den Sketch sowie **Arduino Uno R3**. Diese lokale
Datei ist wegen des später gerätespezifischen seriellen Ports von Git
ausgenommen. Auf einem neuen Rechner kann sie mit folgendem Inhalt
wiederhergestellt werden:

```json
{
  "sketch": "arduino/sorter_test/sorter_test.ino",
  "board": "arduino:avr:uno"
}
```

1. Arduino stromlos in die echte 0°-Stellung beider Klappen bringen. Flap 1
   wird beim Einschalten sofort bestromt; Flap 2 bei 0° nicht.
2. Uno R3 mit einem **USB-Datenkabel** verbinden. In VS Code dieses Repository
   öffnen, `arduino/sorter_test/sorter_test.ino` öffnen und über
   **Arduino: Select Serial Port** den neu angezeigten `/dev/cu.*`-Port
   wählen. **Arduino: Verify** kompiliert, **Arduino: Upload** lädt den
   Sketch hoch. Alternativ kann der Sketch in der Arduino IDE geöffnet
   werden. Nicht versehentlich den Bluetooth- oder Debug-Port auswählen.
3. Im Repository die UI-Abhängigkeit installieren und das Fenster starten:

   ```bash
   .venv/bin/python -m pip install -r arduino/requirements.txt
   .venv/bin/python arduino/control_ui.py
   ```

   In VS Code geht es auch ohne eigenen Terminalbefehl über
   **Terminal → Run Task… → Arduino: Steuerfenster starten**. Diese
   Projekt-Task übergibt Python und Skriptpfad getrennt und funktioniert
   deshalb auch bei Leerzeichen im Projektpfad. Falls du den Befehl selbst
   eingibst, keine zusätzlichen Anführungszeichen *innerhalb* des
   Skriptarguments setzen.

   Ein Python mit Tk-Unterstützung ist nötig (`.venv/bin/python -m tkinter`
   prüft das). Beim Homebrew-Python 3.12 kann dafür
   `brew install python-tk@3.12` erforderlich sein. Den Arduino Serial
   Monitor vor dem Verbinden schließen, da nur
   ein Programm den Port öffnen kann.
4. Im Fenster den seriellen Port wählen und verbinden. Ein Uno kann dabei
   neu starten. Nach `READY` und `POS` die echte 0°-Startlage prüfen und
   das Kontrollkästchen bestätigen; dann werden die Bewegungsbuttons aktiv.

`Paper` bewegt Flap 1 auf +90° und Flap 2 auf den konfigurierten Öffnungswinkel
(anfangs +30°), wartet eine Sekunde und fährt beide zurück. `General` bewegt
nur Flap 1 auf +90°, `Recycling` auf −90°, jeweils mit Rückfahrt. Ein
Sortierablauf startet nur, wenn beide Schrittzähler 0 melden. Die Einzelbuttons
fahren Flap 1 auf +90°, −90° oder 0° und Flap 2 auf seinen Öffnungswinkel oder
0°. Die Schrittbuttons ändern um 10 Vollschritte (ca. 1,8°). `Stopp` hält
eine laufende Schrittfolge an; anschließend müssen die Klappen kontrolliert
und gegebenenfalls einzeln zurückgefahren werden.

Die Nullpunkt-Buttons **bewegen keine Klappe**: sie setzen nur den jeweiligen
Schrittzähler auf 0. Nur benutzen, wenn die echte Stellung geprüft wurde.
Auch nach Arduino-Reset gilt die aktuelle Stellung ungeprüft als 0°.
Die angezeigten Winkel sind aus gesendeten Schritten berechnet, **nicht
gemessen**. Bei Schrittverlust, mechanischem Schlupf, Getriebespiel oder
falscher Initialstellung sind sie ungenau. Für echte Winkelrückmeldung
sind Referenzschalter oder Winkelsensoren nötig. Der Sketch hat keine
mechanischen Endschalter; die Softwaregrenzen von ±90° bzw. ±30° beziehen
sich nur auf den angenommenen Nullpunkt.

Seriell bei 9600 Baud: `P/G/R` = Sortierabläufe, `1/2/0` = Flap 1 direkt,
`3/4` = Flap 2 auf/zu, `+/-` und `>/<` = kleine Schritte,
`Z/X` = Zähler nullen, `!` = Stopp, `?` = Status.
Die bisherigen Befehle `A/B/C/D` bleiben erhalten. Der Sketch sendet
`POS <flap1-schritte> <flap2-schritte>` während der Bewegung und am Ende
`DONE` oder `STOPPED`. `ERROR NOT_HOME` weist einen Sortierablauf mit
nicht genullten Schrittzählern zurück.

Quellen für die elektrische Auslegung: [28BYJ-48-5V-Datenblatt](https://www.mouser.com/datasheet/2/813/step_motor_5v_28byj48_datasheet-3412809.pdf),
[ULN2003A-Datenblatt](https://www.ti.com/lit/ds/symlink/uln2003a.pdf),
[Arduino Uno Rev3](https://store.arduino.cc/products/arduino-uno-rev3).
