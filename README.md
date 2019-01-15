<!--

author:   Sebastian Zug & André Dietrich
email:    zug@ovgu.de   & andre.dietrich@ovgu.de
version:  0.0.1
language: de
narrator: Deutsch Female

script:   https://felixhao28.github.io/JSCPP/dist/JSCPP.es5.min.js

@JSCPP.__eval
<script>
  try {
    var output = "";
    JSCPP.run(`@0`, `@1`, {stdio: {write: s => { output += s }}});
    output;
  } catch (msg) {
    var error = new LiaError(msg, 1);

    try {
        var log = msg.match(/(.*)\nline (\d+) \(column (\d+)\):.*\n.*\n(.*)/);
        var info = log[1] + " " + log[4];

        if (info.length > 80)
          info = info.substring(0,76) + "..."

        error.add_detail(0, info, "error", log[2]-1, log[3]);
    } catch(e) {}

    throw error;
    }
</script>
@end


@JSCPP.eval: @JSCPP.__eval(@input, )

@JSCPP.eval_input: @JSCPP.__eval(@input,`@input(1)`)

@output: <pre class="lia-code-stdout">@0</pre>

@output_: <pre class="lia-code-stdout" hidden="true">@0</pre>


script:   https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js

@Rextester.__eval
<script>
//var result = null;
var error  = false;

console.log = function(e){ send.lia("log", JSON.stringify(e), [], true); };

function grep_(type, output) {
  try {
    let re_s = ":(\\d+):(\\d+): "+type+": (.+)";

    let re_g = new RegExp(re_s, "g");
    let re_i = new RegExp(re_s, "i");

    let rslt = output.match(re_g);

    let i = 0;
    for(i = 0; i < rslt.length; i++) {
        let e = rslt[i].match(re_i);

        rslt[i] = { row : e[1]-1, column : e[2], text : e[3], type : type};
    }
    return [rslt];
  } catch(e) {
    return [];
  }
}

$.ajax ({
    url: "https://rextester.com/rundotnet/api",
    type: "POST",
    timeout: 10000,
    data: { LanguageChoice: @0,
            Program: `@input`,
            Input: `@1`,
            CompilerArgs : @2}
    }).done(function(data) {
        if (data.Errors == null) {
            let warnings = grep_("warning", data.Warnings);

            let stats = "\n-------Stat-------\n"+data.Stats.replace(/, /g, "\n");

            if(data.Warnings)
              stats = "\n-------Warn-------\n"+data.Warnings + stats;

            send.lia("log", data.Result+stats, warnings, true);
            send.lia("eval", "LIA: stop");

        } else {
            let errors = grep_("error", data.Errors);

            let stats = "\n-------Stat-------\n"+data.Stats.replace(/, /g, "\n");

            if(data.Warning)
              stats = data.Errors + data.Warnings + stats;
            else
              stats = data.Errors + data.Warnings + stats;

            send.lia("log", stats, errors, false);
            send.lia("eval", "LIA: stop");
        }
    }).fail(function(data, err) {
        send.lia("log", err, [], false);
        send.lia("eval", "LIA: stop");
    });

"LIA: wait"
</script>
@end


@Rextester.eval: @Rextester.__eval(6, ,"-Wall -std=gnu99 -O2 -o a.out source_file.c")

@Rextester.eval_params: @Rextester.__eval(6, ,"@0")

@Rextester.eval_input: @Rextester.__eval(6,`@input(1)`,"-Wall -std=gnu99 -O2 -o a.out source_file.c")

-->

# Vortrag "Einführung in die technische Realisierung von Automaten"

**Samuel-von-Pufendorf-Gymnasiums, 1. Februar 2019**

Prof. Dr. Sebastian Zug, Technische Universität Bergakademie Freiberg

------------------------------

![Welcome](images/WorkingDesk.jpg "Experiments")<!-- width="80%" -->


Herzlich Willkommen!

## 1. Einführung

Studium der Angewandten Informatik an der Technischen Bergakademie Freiberg

## 2. Motivation des Beispiels

Wieviel Informatik steckt in einer Ampel?

### Analyse des Systems

Geben Sie die Phasen einer Ampel wieder, welche der Zeitphasen sind durch die StVZO geregelt und welche können frei gewählt werden?

<!--
style="width: 80%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
````
                   1      2         3      4       Zustand

                  .-.     .-.      .-.     .-.
  Rot            ( X )   ( X )    (   )   (   )
                  '-'     '-'      '-'     '-'
                  .-.     .-.      .-.     .-.
  Gelb           (   )   ( X )    (   )   ( X )
                  '-'     '-'      '-'     '-'
                  .-.     .-.      .-.     .-.
  Grün           (   )   (   )    ( X )   (   )
                  '-'     '-'      '-'     '-'

               .-> 2s ---> 2s ---> 100s ---> 2s -.
               |                                 |
               .---------------------------------.
````

### Technische Realsierung

<!--
style="width: 70%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
````
  EINGABEN                         AUSGABEN

  __|____
               ┌-----------┐
        2S  -->|           |
      100S  -->|  Ampel-   |
               |           |---*--> Rot
          .--->|           |--*+--> Gelb
          |.-->| steuerung |-*++--> Grün
          ||.->|           | |||
          |||  └-----------┘ |||
          ||'----------------'||
          |'------------------'|
          '--------------------'
````

Eingaben: 2_s beendet und 100_s bedendet
Ausgaben: Rot an, Gelb an, Grün an

## 3. Entwurf des Automaten

### Idee





### ... angewandt auf die Ampel
<!--
style="width: 80%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
````
                             Transitionen

                   .-- 2s --. .-- 2s --. .- 100s -.
                   |        v |        v |        v
                  .-.       .-.        .-.       .-.
Ampelzustände    ( 0 )     ( 1 )      ( 2 )     ( 3 )
                  '-'       '-'        '-'       '-'
                   ^                              |
                   .------------- 2s -------------.
````

__Schrittweises einblenden der Tabelle!__

| 2_s | 100_s |  Zustand  | Zustand' |
|  0  |  0    |    0      |   0      |
|  0  |  0    |    1      |   1      |
|  0  |  0    |    2      |   2      |
|  0  |  0    |    3      |   3      |
|  0  |  1    |    0      |   0      |
|  0  |  1    |    1      |   1      |
|  0  |  1    |    2      |   3      |
|  0  |  1    |    3      |   3      |
|  1  |  0    |    ...    |   ...    |

Abbildung der Zustände durch einen binären Speicher (Flip-Flop)

| Zustand | FF2      | FF1     |
|:--------|:---------|:--------|
|  0      |   0      |   0     |
|  1      |   0      |   1     |
|  2      |   1      |   0     |
|  3      |   1      |   1     |

| Zustand | FF2      | FF1     |  Rot    | Gelb     | Grün    |
|:--------|:---------|:--------|:--------|:---------|:--------|
|  0      |   0      |   0     |  1      |   0      |   0     |
|  1      |   0      |   1     |  1      |   1      |   0     |
|  2      |   1      |   0     |  0      |   0      |   1     |
|  3      |   1      |   1     |  0      |   1      |   0     |

Rot = !FF2 und !FF1 oder !FF2 und FF1 = !FF2
Gelb = !FF2 und FF1 oder FF2 und FF1 = FF1
Grün = FF2 und !FF1

Zwischenstand



Übertragung auf die Zustandstabelle

| 2_s | 100_s |  FF2  | FF1  |
|  0  |  0    |   0   |   0  |
|  0  |  0    |   0   |   1  |
|  0  |  0    |   1   |   0  |
|  0  |  0    |   1   |   1  |
|  0  |  1    |   0   |   0  |
|  0  |  1    |   0   |   0  |

| 2_s | 100_s |  FF2  | FF1  |  FF2' | FF1' |
|  0  |  0    |   0   |   0  |   0   |   0  |
|  0  |  0    |   0   |   1  |   0   |   1  |
|  0  |  0    |   1   |   0  |   1   |   0  |
|  0  |  0    |   1   |   1  |   1   |   1  |
|  0  |  1    |   0   |   0  |   0   |   0  |
|  0  |  1    |   0   |   0  |   0   |   0  |

Welche Einträge sind denn überhaupt relevant?

| 2_s | 100_s |  FF2  | FF1  |  FF2' | FF1' |
|  0  |  1    |   1   |   0  |   1   |   1  |
|  1  |  0    |   0   |   0  |   0   |   1  |
|  1  |  0    |   0   |   1  |   1   |   0  |
|  1  |  0    |   1   |   1  |   0   |   0  |

FF2' = !2_s und 100_s und FF2 und !FF1 oder
        2_s und !100_s und !FF2 und FF1

FF1' = !2_s und 100_s und FF2 und !FF1 oder
       2_s und !100_s und !FF2 und !FF1

## 4. Realsierung in der Simulation

Warum brauchen wir einen Takt?


## 5. Umsetzung auf dem Steckbrett

## 6. Zusammenfassung und Ausblick

Ablauf beim Aufstellen eines Automaten

1. Analyse des Systems, Identifikation von Eingängen, Ausgängen und Zuständen
2. Modellierung als Automat
3. Aufstellen der Wahrheitstafel
4. Ableiten der Schaltfunktionen
5. Realisieren des Schaltwerkes

Mängel unserer Lösung
