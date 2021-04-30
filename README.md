<!--

author:   Sebastian Zug & André Dietrich
email:    zug@ovgu.de   & andre.dietrich@ovgu.de
version:  1.1.2
language: de
narrator: Deutsch Female

import: https://raw.githubusercontent.com/liaTemplates/logicemu/master/README.md
        https://github.com/LiaTemplates/AVR8js/main/README.md#10
        https://raw.githubusercontent.com/LiaTemplates/DigiSim/master/README.md
        https://github.com/LiaTemplates/Pyodide
-->

# Vortrag "Anwendung von boolschen Funktionen"

**Samuel-von-Pufendorf-Gymnasiums, Flöha, 24. Januar 2020**

Prof. Dr. Sebastian Zug, Technische Universität Bergakademie Freiberg

------------------------------

![Welcome](images/WorkingDesk.jpg "Experiments")<!-- height=70%" -->

Code des Vortrages https://github.com/SebastianZug/StateMachines
Präsentationsmodus [Link](https://liascript.github.io/course/?https://raw.githubusercontent.com/SebastianZug/StateMachines/master/README.md#1)

## 1. Einführung

Studium der Angewandten Informatik an der Technischen Bergakademie Freiberg

* Angewandte Informatik
* Robotik
* Internet der Energie

https://tu-freiberg.de/fakult1/inf

![Welcome](images/AInfFreiberg.jpeg)<!-- width="80%" -->

*"Hacken kann jeder, da brauche ich kein \[Informatik-\] Studium"* \[Forenbeitrag\]

## 2. Motivation des Beispiels

Wie viel Informatik steckt in einer Lichtsignalanlage (Verkehrsampel)?

![Welcome](images/AmpelDresden-klein.jpg)<!-- width="80%" -->

__Zielstellung__:
* Koordination des Verkehrs auf einer Kreuzung / Verkehrslenkung
* Informatiksicht: Zugangsberechtigung für eine Ressource (Kreuzung)

__Technische Herausforderungen__:
* Vernetzung und Koordination der Ampeln selbst,
* Adaption des Verhaltens
* Interaktion mit den Verkehrsteilnehmern

**Wir wollen eine einzige Ampel mit einer Softwarelösung und einer Hardwarelösung umsetzen!**

### Analyse des Systems

Unsere Herausforderung heute ... Implementierung einer einzelnen
Ampelanlage.

![Welcome](images/Ampelsimulation.gif "Ampelablauf")<!-- width="10%" --> [^1]

[^1]:https://wiki.byte-welt.net/wiki/Simulation_einer_Verkehrsampel

Wie würden Sie den Ablauf beschreiben?

+ 4 Phasen - Rot, Rot-Gelb, Grün, Gelb
+ Bestimmte Zeitintervalle dazwischen

<!--
style="width: 80%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
````ascii
                            Zustände
                   0       1       2       3       

                  .-.     .-.     .-.     .-.
  Rot            ( X )   ( X )   (   )   (   )
                  '-'     '-'     '-'     '-'

                  .-.     .-.     .-.     .-.
  Gelb           (   )   ( X )   (   )   ( X )
                  '-'     '-'     '-'     '-'

                  .-.     .-.     .-.     .-.
  Grün           (   )   (   )   ( X )   (   )
                  '-'     '-'     '-'     '-'

             .-> 100s ---> 2s ---> 100s ---> 2s -.
             |                                   |
             .-----------------------------------.
````

Die Einteilung der $100s$ ist hier willkürlich gewählt. Die Wahl dieses Parameters
beeindlusst den Verkehr an der Kreuzung erheblich und variiert üblicherweise über dem Tagesverlauf.

### Zielstellung

Was ist also unser Ziel? Ein System, dass in Abhängigkeit vom aktuellen Zustand
und den Taktimpulsen einen neuen Zustand aktiviert.

<!--
style="width: 70%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
```ascii
 EINGABEN                                  AUSGABEN

 Taktgeber             ╔═══════════╗
 ┴┴┴┴┴┴┴┴┴┴    2S   -->║           ║
 ┴───...──┴  100S   -->║   Ampel-  ║
                       ║           ║───┬──> Rot
                 .---->║           ║──┬┼──> Gelb
                 | .-->║ steuerung ║─┬┼┼──> Grün
                 | |.->║           ║ │││
                 | ||  ╚═══════════╝ |││
                 | |.----------------.|│
                 | .------------------.|
                 .---------------------.
````

Wie entwerfen wir eine Abstraktion, die diese Zusammenhänge abbildet und auf
verschiedenen Hardwareebenen realisierbar ist?


## 3. Entwurf des Automaten

**Einführungsbeispiel**

> __Automat__ Ein endlicher Automat (englisch _finite_ _state_ _machine_) ist ein Modell eines Verhaltens, bestehend aus Zuständen, Zustandsübergängen und Aktionen. Ein Zustand speichert die Information über die Vergangenheit, d. h. er reflektiert in gewissem Umfang die Änderungen der Eingabe seit dem Systemstart bis zum aktuellen Zeitpunkt.

Eine Tür lässt sich zum Beispiel mit zwei Zuständen beschreiben "auf" und "zu"

Bespiel:

<!--
style="width: 100%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
```ascii
                  Zustandsübergang (Transition)

                  .--------- schließen ----------.
                  |                              |
                  |                              v
                 .-.                            .-.
 Zustände       (auf)                          (zu )
                 '-'                            '-'
                  ^                              |
                  |                              |
                  .----------- öffnen -----------.
```

{{1-4}} Der Übergang lässt sich dabei mit einer *Zustandsübergangstabelle* darstellen.

{{1-4}}
| Eingabe $E$   | alter Zustand $Z$ | neuer Zustand $Z'$ |
|:-----------|:--------------|:--------------|
| öffnen     | offen         | offen         |
| öffnen     | zu            | offen         |
| schließen  | offen         | zu            |
| schließen  | zu            | zu            |

{{2-4}} Ausgehend vom Zustand soll nun noch eine Ausgabe erfolgen, zum Beispiel
ein Warnlicht aktiviert werden

{{2-4}}
| Zustand $Z$ | Ausgabe   $A$   |
|:------------|:----------------|
| offen       | Warnlicht       |
| zu          | Warnlicht aus   |

{{3-4}}
> Zusammenfassung: Ein endlicher Automat bildet Eingabegrößen $E$ auf Zustände $Z$
> und Ausgabegrößen $A$ ab.

### ... angewandt auf die Ampel
<!--
style="width: 80%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
```ascii
                  .- 100s -. .-- 2s --. .- 100s -.
                  |        | |        | |        |
                  |        v |        v |        v
                 .-.       .-.        .-.       .-.
 Ampelzustände  ( 0 )     ( 1 )      ( 2 )     ( 3 )
                 '-' Rot   '-' Rot    '-' Grün  '-' Gelb
                  ^            Gelb              |
                  |                              |
                  .------------- 2s -------------.
```
Wie verhält sich unser System für verschiedenen Kombinationen der Variablen 2s und 100s?

{{0-1}} Eingaben $E$

{{0-1}}
* `2s` ... ein Timer generiert kurzzeitig eine  "1", wenn ein 2 Sekundenintervall abgelaufen ist, dazwischen hat der Eingang den Wert "0"
* `100s` ... ein 100-Sekundentimer generiert einen Wert "1"

{{1-4}}
*******************************************************************************
__Welche Zustandsübergänge wollen wir realisieren?__

********************************************************************************

{{1-2}}
<!--data-type="none"-->
| 2s  | 100s  |  Zustand  | Zustand neu |
|:----|:------|:----------|:---------|
|  0  |  0    |    0      |   0      |
|  0  |  0    |    1      |   1      |
|  0  |  0    |    2      |   2      |
|  0  |  0    |    3      |   3      |


{{2-3}}
<!--data-type="none"-->
| 2s  | 100s |  Zustand  | Zustand' |
|:----|:------|:----------|:---------|
| <span style="color:red"> 0 </span> |  <span style="color:red"> 1 </span>     |    <span style="color:red"> 0 </span>       |  <span style="color:red"> 1 </span>      |
|  0  |  1    |    1      |   1      |
| <span style="color:red"> 0 </span> |  <span style="color:red"> 1 </span>     |    <span style="color:red"> 2 </span>       |  <span style="color:red"> 3 </span>      |
|  0  |  1    |    3      |   3      |

{{3-4}}
| 2s  | 100s |  Zustand  | Zustand' |
|:----|:------|:----------|:---------|
|  1  |  0    |    0      |   0      |
| <span style="color:red"> 1</span> |  <span style="color:red"> 0 </span>     |    <span style="color:red"> 1 </span>       |  <span style="color:red"> 2 </span>      |
|  1  |  0    |    2      |   2      |
| <span style="color:red"> 1</span> |  <span style="color:red"> 0 </span>     |    <span style="color:red"> 3 </span>       |  <span style="color:red"> 0 </span>      |

{{4-5}}
Die Kombination `2_s = 1` und `100s = 1` bleibt hier unbeachtet. Welches Problem sehen Sie, dass wir hier noch lösen müssen?

### Jetzt wird es digital

> Für die Repräsentation der Zustände nutzen wir digitale Speicher - **Flip-Flops**.
> Folglich müssen unsere Zustande auch mit `0` und `1` codiert werden.

Abbildung der Zustände durch einen binären Speicher, sogen. Flip-Flops (FF), wobei ein
einzelner Flip-Flop ein Bit, also zwei unterschiedliche Zustände speichern
kann.

> Testen Sie das Verhalten an einer kleinen Simulation eines D-Flip-Flops!

``` json @DigiSim.evalJson
{"devices":{"dev0":{"label":"data","type":"Button","propagation":0,"position":{"x":0,"y":37.5}},"dev1":{"label":"clock","type":"Button","propagation":0,"position":{"x":0,"y":95}},"dev2":{"label":"D-Flipflop","type":"Dff","propagation":0,"polarity":{"clock":true},"bits":1,"initial":"x","position":{"x":125,"y":60}},"dev3":{"label":"Output","type":"Lamp","propagation":0,"position":{"x":270,"y":55}}},"connectors":[{"from":{"id":"dev0","port":"out"},"to":{"id":"dev2","port":"in"}},{"from":{"id":"dev1","port":"out"},"to":{"id":"dev2","port":"clk"}},{"from":{"id":"dev2","port":"out"},"to":{"id":"dev3","port":"in"}}],"subcircuits":{}}
```

Wie viele Flip-Flops brauchen wir für unsere Ampel?

{{1-3}}
<!--
style="width: 80%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
```ascii
                  .- 100s -. .-- 2s --. .- 100s -.
                  |        | |        | |        |
                  |        v |        v |        v
                 .-.       .-.        .-.       .-.
 Ampelzustände  ( 0 )     ( 1 )      ( 2 )     ( 3 )
                 '-'\     /'-'        '-'\     /'-'
                  ^   FF1                  FF2   |
                  |                              |
                  .------------- 2s -------------.
```

{{2-3}}
<!--data-type="none"-->
| Ampelphase | Zustand | FF2      | FF1     |
|:-----------|:--------|:---------|:--------|
| Rot        |  0      |   0      |   0     |
| Rot-Gelb   |  1      |   0      |   1     |
| Grün       |  2      |   1      |   0     |
| Gelb       |  3      |   1      |   1     |

### Ableitung der Gleichungen

Soweit so gut, aber wie können wir ein System entwerfen, dass
* zwischen diesen Zuständen entsprechend den Eingaben wechselt
* die Ausgaben generiert

Noch mal die Idee ...

<!--
style="width: 70%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
```ascii
 EINGABEN E              CLOCK C           AUSGABEN A
                            |
                            v
 Taktgeber            ╔═══════════╗
 ┴┴┴┴┴┴┴┴┴┴    2S  -->║           ║──────> Rot
 ┴───...──┴  100S  -->║   Ampel-  ║──────> Gelb
                      ║           ║──────> Grün
                  .-->║   Logik   ║--. FF1
                  |.->║           ║-.| FF2
                  ||  ╚═══════════╝ |│
  ZUSTAND' Z'     |'----------------╯|
                  '------------------.
```
$$A = f(Z)$$
$$Z' = Z + E$$


{{1-3}}
** Schritt 1 - Ausgabefunktionen A**

{{1-3}}
<!--data-type="none"-->
| Zustand | FF2      | FF1     |  A_Rot  | A_Gelb   | A_Grün  |
|:--------|:---------|:--------|:--------|:---------|:--------|
|  0      |   0      |   0     |  1      |   0      |   0     |
|  1      |   0      |   1     |  1      |   1      |   0     |
|  2      |   1      |   0     |  0      |   0      |   1     |
|  3      |   1      |   1     |  0      |   1      |   0     |

{{2-3}}
$$A_{Rot} = (\overline{FF_2} \cdot \overline{FF_1}) + (\overline{FF_2} \cdot FF_1) = \overline{FF_2}$$
$$A_{Gelb} = (\overline{FF_2} \cdot FF_1) + (FF_2 \cdot FF_1) = FF_1$$
$$A_{Grün} = FF_2 \cdot \overline{FF_1}$$

{{3-6}}
** Schritt 2 - Zustandsübergangsfunktion Z**

{{3-4}}
<!--data-type="none"-->
| 2_s | 100_s | Z |Z'  |
| 0   | 0     | 0 | 0  |
| 0   | 0     | 1 | 1  |
| 0   | 0     | 2 | 2  |
| 0   | 0     | 3 | 3  |
| 0   | 1     | 0 | 1  |
| 0   | 1     | 1 | 1  |
| 0   | 1     | 2 | 3  |
| 0   | 1     | 3 | 3  |
| 1   | 0     | 0 | 0  |
| 1   | 0     | 1 | 2  |
| 1   | 0     | 2 | 2  |
| 1   | 0     | 3 | 0  |


{{4-6}}
<!--data-type="none"-->
| 2_s | 100_s | Z | Z' | FF2 | FF1 | FF2' | FF1' |
| 0   | 0     | 0 | 0  | 0   | 0   | 0    | 0    |
| 0   | 0     | 1 | 1  | 0   | 1   | 0    | 1    |
| 0   | 0     | 2 | 2  | 1   | 0   | 1    | 0    |
| 0   | 0     | 3 | 3  | 1   | 1   | 1    | 1    |
| 0   | 1     | 0 | 1  | 0   | 0   | 0    | 1    |
| 0   | 1     | 1 | 1  | 0   | 1   | 0    | 1    |
| 0   | 1     | 2 | 3  | 1   | 0   | 1    | 1    |
| 0   | 1     | 3 | 3  | 1   | 1   | 1    | 1    |
| 1   | 0     | 0 | 0  | 0   | 0   | 0    | 0    |
| 1   | 0     | 1 | 2  | 0   | 1   | 1    | 0    |
| 1   | 0     | 2 | 2  | 1   | 0   | 1    | 0    |
| 1   | 0     | 3 | 0  | 1   | 1   | 0    | 0    |

{{5-6}}
Wie kann man diese Wertetabellen minimieren? Nur vier Eingangsgrößen? Das lässt sich gut mit dem Karnaught-Veitch Diagramm lösen!

{{6-7}}
<!--
style="width: 60%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
```ascii
                 __              __
                 2s    2s   2s   2s
                ____ ____
                100s 100s 100s 100s   
   ___    ___  +----+----+----+----+
   FF1    FF2  |    |    |    |    |
          ___  +----+----+----+----+
   FF1    FF2  |    |    |    |    |
               +----+----+----+----+
   FF1    FF2  |    |    |    |    |
   ___         +----+----+----+----+
   FF1    FF2  |    |    |    |    |
               +----+----+----+----+
```

{{7-8}}
********************************************************************************
<!--
style="width: 60%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
```ascii
                 __              __
                 2s    2s   2s   2s
                ____ ____
                100s 100s 100s 100s   
   ___    ___  +----+----+----+----+
   FF1    FF2  |    |    |    |    |
          ___  +----+----+----+----+
   FF1    FF2  |    |  1 |    |    |
               +----+----+----+----+
   FF1    FF2  |  1 |    |    |  1 |
   ___         +----+----+----+----+
   FF1    FF2  |  1 |  1 |    |  1 |
               +----+----+----+----+
```

Als Lösung ergibt sich entsprechend:

$$FF_2' =(FF_2 \cdot \overline{2s}) + (\overline{100s} \cdot FF_2 \cdot \overline{FF_1}) + (2s \cdot \overline{100s} \cdot FF_1 \cdot \overline{FF_2})$$

> __Aufgabe__: Vereinfachen Sie die Darstellung von $FF1'$ analog mit dem Karnaught-Veitch Diagramm.

********************************************************************************

         {{8-9}}
******************************************************************************
Ok, eine Menge Arbeit, dass muss doch auch einfacher gehen! Wir nutzen eine Python-Bibliothek um diese Aufgabe effizienter zu realisieren. Das folgende Skript übernimmt diese Aufgabe. Verändern Sie probeweise die `FF1_minterms` und die `FF2_minterms` Definitionen.

```python       solveBoolFunc.py
from sympy.logic import SOPform
from sympy import symbols
from sympy import printing

x3, x2, x1, x0 = symbols('2s 100s FF2 FF1')

FF1_minterms = [[0, 0, 0, 1],
                [0, 0, 1, 1],
                [0, 1, 0, 0],
                [0, 1, 0, 1],
                [0, 1, 1, 0],
                [0, 1, 1, 1],]
result = SOPform([x3, x2, x1, x0], FF1_minterms)
print("FF1 = " + (printing.ccode(result)))

FF2_minterms = [[0, 0, 1, 0],
                [0, 0, 1, 1],
                [0, 1, 1, 0],
                [0, 1, 1, 1],
                [1, 0, 0, 1],
                [1, 0, 1, 0],]
result = SOPform([x3, x2, x1, x0], FF2_minterms)
print("FF2 = " + (printing.ccode(result)))
```
@Pyodide.eval


$$FF_1' =  (\overline{2s} \cdot 100s) + (FF_1 \cdot \overline{2s})$$
$$FF_2' =(FF_2 \cdot \overline{2s}) + (\overline{100s} \cdot FF_2 \cdot \overline{FF_1}) + (2s \cdot \overline{100s} \cdot FF_1 \cdot \overline{FF_2})$$

******************************************************************************

## 4. Realsierung

Eine der großen Herausforderungen in jedem Projekt ist die Wahl der geeigneten Umsetzungsebene. Welche Formate bieten sich für unser Projekt an?

| Methode           | Bauteilkosten    | Entwurf        | Variabilität   |
|:------------------|:-----------------|:---------------|:---------------|
| Analoge Schaltung | minimal          | aufwändig      | gering         |
| Digitale Logik    | gering           | einfach        | mittel         |
| Software (eingebetteter $\mu$C) | überschaubar | einfach | hoch         |
| Software (PC)     | hoch        | sehr einfach | hoch   |

### ... mit ICs (zumindest in der Simulation)

$$A_{Rot} = \overline{FF_2}; A_{Gelb} = FF_1; A_{Grün} = FF_2 \cdot \overline{FF_1}$$
$$FF_1 =(FF_1 \cdot \overline{2s}) + (\overline{2s} \cdot 100s)$$
$$FF_2 =(FF_2 \cdot \overline{2s}) + (\overline{100s} \cdot FF_2 \cdot \overline{FF_1}) + (2s \cdot \overline{100s} \cdot FF_1 \cdot \overline{FF_2})$$

Warum brauchen wir einen Takt?


Bitte am Anfang s2 und s100 ein schalten und einen clock puls auslösen, um den Startzustand her zu stellen.

```json @DigiSim.evalJson
{"devices":{"s2":{"label":"s2","type":"Button","propagation":0,"position":{"x":0,"y":35}},"s100":{"label":"s100","type":"Button","propagation":0,"position":{"x":20,"y":125}},"clk":{"label":"clk","type":"Button","propagation":0,"position":{"x":595,"y":145}},"rot":{"label":"rot","type":"Lamp","propagation":1,"position":{"x":1100,"y":15}},"gelb":{"label":"gelb","type":"Lamp","propagation":1,"position":{"x":1100,"y":90}},"gruen":{"label":"gruen","type":"Lamp","propagation":1,"position":{"x":1100,"y":170}},"not1":{"label":"not1","type":"Not","propagation":1,"bits":1,"position":{"x":125,"y":25}},"not2":{"label":"not2","type":"Not","propagation":1,"bits":1,"position":{"x":105,"y":105}},"not3":{"label":"not3","type":"Not","propagation":1,"bits":1,"position":{"x":105,"y":185}},"not4":{"label":"not4","type":"Not","propagation":1,"bits":1,"position":{"x":120,"y":285}},"f":{"label":"FF2","type":"Dff","propagation":1,"polarity":{"clock":true},"bits":1,"initial":"x","position":{"x":795,"y":55}},"g":{"label":"FF1","type":"Dff","propagation":1,"polarity":{"clock":true},"bits":1,"initial":"x","position":{"x":760,"y":135}},"and1":{"label":"and1","type":"And","propagation":1,"bits":1,"position":{"x":265,"y":-30}},"and2":{"label":"and2","type":"And","propagation":1,"bits":1,"position":{"x":260,"y":35}},"and3":{"label":"and3","type":"And","propagation":1,"bits":1,"position":{"x":410,"y":20}},"and4":{"label":"and4","type":"And","propagation":1,"bits":1,"position":{"x":280,"y":100}},"and5":{"label":"and5","type":"And","propagation":1,"bits":1,"position":{"x":955,"y":165}},"and6":{"label":"and6","type":"And","propagation":1,"bits":1,"position":{"x":280,"y":275}},"and7":{"label":"and7","type":"And","propagation":1,"bits":1,"position":{"x":280,"y":215}},"and8":{"label":"and8","type":"And","propagation":1,"bits":1,"position":{"x":280,"y":155}},"and9":{"label":"and9","type":"And","propagation":1,"bits":1,"position":{"x":435,"y":125}},"or1":{"label":"or1","type":"Or","propagation":1,"bits":1,"position":{"x":555,"y":0}},"or2":{"label":"or2","type":"Or","propagation":1,"bits":1,"position":{"x":620,"y":80}},"or3":{"label":"or3","type":"Or","propagation":1,"bits":1,"position":{"x":540,"y":195}}},"connectors":[{"from":{"id":"s2","port":"out"},"to":{"id":"not1","port":"in"}},{"from":{"id":"s100","port":"out"},"to":{"id":"not2","port":"in"}},{"from":{"id":"f","port":"out"},"to":{"id":"not3","port":"in"},"vertices":[{"x":890,"y":395},{"x":85,"y":395}]},{"from":{"id":"g","port":"out"},"to":{"id":"not4","port":"in"},"vertices":[{"x":600,"y":365}]},{"from":{"id":"or2","port":"out"},"to":{"id":"f","port":"in"}},{"from":{"id":"or1","port":"out"},"to":{"id":"or2","port":"in1"}},{"from":{"id":"and3","port":"out"},"to":{"id":"or1","port":"in2"}},{"from":{"id":"and2","port":"out"},"to":{"id":"and3","port":"in2"}},{"from":{"id":"and1","port":"out"},"to":{"id":"or1","port":"in1"}},{"from":{"id":"and4","port":"out"},"to":{"id":"and9","port":"in1"}},{"from":{"id":"and8","port":"out"},"to":{"id":"and9","port":"in2"}},{"from":{"id":"or3","port":"out"},"to":{"id":"g","port":"in"}},{"from":{"id":"and9","port":"out"},"to":{"id":"or2","port":"in2"}},{"from":{"id":"and7","port":"out"},"to":{"id":"or3","port":"in1"}},{"from":{"id":"and6","port":"out"},"to":{"id":"or3","port":"in2"}},{"from":{"id":"not1","port":"out"},"to":{"id":"and1","port":"in1"}},{"from":{"id":"f","port":"out"},"to":{"id":"and1","port":"in2"},"vertices":[{"x":900,"y":395},{"x":85,"y":395},{"x":120,"y":245},{"x":220,"y":220}]},{"from":{"id":"not2","port":"out"},"to":{"id":"and3","port":"in1"}},{"from":{"id":"f","port":"out"},"to":{"id":"and2","port":"in1"},"vertices":[{"x":900,"y":395},{"x":85,"y":395},{"x":120,"y":245},{"x":220,"y":170}]},{"from":{"id":"not4","port":"out"},"to":{"id":"and2","port":"in2"}},{"from":{"id":"s2","port":"out"},"to":{"id":"and4","port":"in1"}},{"from":{"id":"not2","port":"out"},"to":{"id":"and4","port":"in2"}},{"from":{"id":"not3","port":"out"},"to":{"id":"and8","port":"in1"}},{"from":{"id":"g","port":"out"},"to":{"id":"and8","port":"in2"},"vertices":[{"x":595,"y":365},{"x":230,"y":365},{"x":230,"y":335}]},{"from":{"id":"not1","port":"out"},"to":{"id":"and7","port":"in1"}},{"from":{"id":"g","port":"out"},"to":{"id":"and7","port":"in2"},"vertices":[{"x":660,"y":365},{"x":240,"y":365}]},{"from":{"id":"clk","port":"out"},"to":{"id":"f","port":"clk"}},{"from":{"id":"clk","port":"out"},"to":{"id":"g","port":"clk"}},{"from":{"id":"not1","port":"out"},"to":{"id":"and6","port":"in1"}},{"from":{"id":"s100","port":"out"},"to":{"id":"and6","port":"in2"},"vertices":[{"x":100,"y":140},{"x":40,"y":225}]},{"from":{"id":"f","port":"out"},"to":{"id":"and5","port":"in1"}},{"from":{"id":"not4","port":"out"},"to":{"id":"and5","port":"in2"},"vertices":[{"x":390,"y":335}]},{"from":{"id":"not3","port":"out"},"to":{"id":"rot","port":"in"},"vertices":[{"x":210,"y":415},{"x":920,"y":415}]},{"from":{"id":"g","port":"out"},"to":{"id":"gelb","port":"in"}},{"from":{"id":"and5","port":"out"},"to":{"id":"gruen","port":"in"}}],"subcircuits":{}}
```

### ... in Software

Das folgende Beispiel zeigt die Implementierung in C für einen Arduino Uno (Atmega 328 Controller). Führen Sie den Code aus und erklären Sie anhand des Codes, wie unser Ampelautomat sich hier wiederfindet.

<div>
  <wokwi-led color="red" pin="13" port="B" label="13"></wokwi-led>
  <wokwi-led color="yellow" pin="12" port="B" label="12"></wokwi-led>
  <wokwi-led color="green" pin="11" port="B" label="11"></wokwi-led>
  <span id="simulation-time"></span>
</div>
```cpp       arduino.cpp
typedef struct {
    int state;
    int next;
    int A_red;
    int A_yellow;
    int A_green;
    int timer;
} tl_state_t;    // Traffic light state

tl_state_t states[4] = {

// state     A_red             timer
//  |   next  |  A_yellow       |
//  |    |    |   |    A_green  |
//----------------------------------------------
{   0,   1,   1,  0,    0,      3},
{   1,   2,   1,  1,    0,      1 },
{   2,   3,   0,  0,    1,      3},
{   3,   0,   0,  1,    0,      1,}
};

const int greenPin = 11;
const int yellowPin = 12;
const int redPin = 13;
int state = 0;

void setup() {
  pinMode(greenPin, OUTPUT);
  pinMode(yellowPin, OUTPUT);
  pinMode(redPin, OUTPUT);
}

void loop() {
  if (states[state].A_red == 1) digitalWrite(redPin, HIGH);
  else digitalWrite(redPin, LOW);
  if (states[state].A_yellow == 1) digitalWrite(yellowPin, HIGH);
  else digitalWrite(yellowPin, LOW);
  if (states[state].A_green == 1) digitalWrite(greenPin, HIGH);
  else digitalWrite(greenPin, LOW);
  delay(states[state].timer*1000);
  state =  states[state].next;
}
```
@AVR8js.sketch

## 5. Zusammenfassung und Ausblick

__Ablauf beim Aufstellen eines Automaten__

1. Analyse des Systems, Identifikation von Eingängen, Ausgängen und Zuständen
2. Modellierung als Automat
3. Aufstellen der Wahrheitstafel
4. Ableiten der Schaltfunktionen
5. Realisieren in Hardware oder Software

__Mängel oder Fragen hinsichtlich unserer Lösung__
* Keine Berücksichtigung von gleichzeitig aktivem 2s und 100s
* Wie setzen wir die Timer um?

... diese Fragen beantworten wir dann im Rahmen Ihres Studiums :-)


<!--
style="width: 80%; max-width: 660px; display: block; margin-left: auto; margin-right: auto;"
-->
```ascii
+=============================================================+
| Informationstage / Schnupper-Events an der TU Bergakademie  |
|    * Girlsday (26.03.2020)                                  |
|    * Frühjahrsakademie (24.02. - 28.02.2020)                |
|    * Campustag (16.05.2020)                                 |
+=============================================================+
```
