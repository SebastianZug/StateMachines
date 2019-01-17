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


@logic_emu: @logic_emu_(@uid)

@logic_emu_
<script>
/** @constructor */
function LZ77Coder() {
  this.lz77MatchLen = function(text, i0, i1) {
    var l = 0;
    while(i1 + l < text.length && text[i1 + l] == text[i0 + l] && l < 255) {
      l++;
    }
    return l;
  };

  this.encodeString = function(text) {
    return arrayToString(this.encode(stringToArray(text)));
  };

  this.decodeString = function(text) {
    return arrayToString(this.decode(stringToArray(text)));
  };

  // Designed mainly for 7-bit ASCII text. Although the text array may contain values
  // above 127 (e.g. unicode codepoints), only values 0-127 are encoded efficiently.
  this.encode = function(text) {
    var result = [];
    var map = {};

    var encodeVarint = function(i, arr) {
      if(i < 128) {
        arr.push(i);
      } else if(i < 16384) {
        arr.push(128 | (i & 127));
        arr.push(i >> 7);
      } else {
        arr.push(128 | (i & 127));
        arr.push(128 | ((i >> 7) & 127));
        arr.push((i >> 14) & 127);
      }
    };

    for(var i = 0; i < text.length; i++) {
      var len = 0;
      var dist = 0;

      var sub = arrayToStringPart(text, i, 4);
      var s = map[sub];
      if(s) {
        for(var j = s.length - 1; j >= 0; j--) {
          var i2 = s[j];
          var d = i - i2;
          if(d > 2097151) break;
          var l = this.lz77MatchLen(text, i2, i);
          if(l > len) {
            len = l;
            dist = d;
            if(l > 255) break; // good enough, stop search
          }
        }
      }

      if(len > 2097151) len = 2097151;

      if(!(len > 5 || (len > 4 && dist < 16383) || (len > 3 && dist < 127))) {
        len = 1;
      }

      for(var j = 0; j < len; j++) {
        var sub = arrayToStringPart(text, i + j, 4);
        if(!map[sub]) map[sub] = [];
        if(map[sub].length > 1000) map[sub] = []; // prune
        map[sub].push(i + j);
      }
      i += len - 1;

      if(len >= 3) {
        if(len < 130) {
          result.push(128 + len - 3);
        } else {
          var len2 = len - 128;
          result.push(255);
          encodeVarint(len2, result);
        }
        encodeVarint(dist, result);
      } else {
        var c = text[i];
        if(c < 128) {
          result.push(c);
        } else {
          // Above-ascii character, encoded as unicode codepoint (not UTF-16).
          // Normally such character does not appear in circuits, but it could in comments.
          result.push(255);
          encodeVarint(c - 128, result);
          result.push(0);
        }
      }
    }
    return result;
  };

  this.decode = function(encoded) {
    var result = [];
    var temp;
    for(var i = 0; i < encoded.length;) {
      var c = encoded[i++];
      if(c > 127) {
        var len = c + 3 - 128;
        if(c == 255) {
          len = encoded[i++];
          if(len > 127) len += (encoded[i++] << 7) - 128;
          if(len > 16383) len += (encoded[i++] << 14) - 16384;
          len += 128;
        }
        dist = encoded[i++];
        if(dist > 127) dist += (encoded[i++] << 7) - 128;
        if(dist > 16383) dist += (encoded[i++] << 14) - 16384;

        if(dist == 0) {
          result.push(len);
        } else {
          for(var j = 0; j < len; j++) {
            result.push(result[result.length - dist]);
          }
        }
      } else {
        result.push(c);
      }
    }
    return result;
  };
}
function arrayToString(a) {
  var s = '';
  for(var i = 0; i < a.length; i++) {
    //s += String.fromCharCode(a[i]);
    var c = a[i];
    if (c < 0x10000) {
       s += String.fromCharCode(c);
    } else if (c <= 0x10FFFF) {
      s += String.fromCharCode((c >> 10) + 0xD7C0);
      s += String.fromCharCode((c & 0x3FF) + 0xDC00);
    } else {
      s += ' ';
    }
  }
  return s;
}
function stringToArray(s) {
  var a = [];
  for(var i = 0; i < s.length; i++) {
    //a.push(s.charCodeAt(i));
    var c = s.charCodeAt(i);
    if (c >= 0xD800 && c <= 0xDBFF && i + 1 < s.length) {
      var c2 = s.charCodeAt(i + 1);
      if (c2 >= 0xDC00 && c2 <= 0xDFFF) {
        c = (c << 10) + c2 - 0x35FDC00;
        i++;
      }
    }
    a.push(c);
  }
  return a;
}
// ignores the utf-32 unlike arrayToString but that's ok for now
function arrayToStringPart(a, pos, len) {
  var s = '';
  for(var i = pos; i < pos + len; i++) {
    s += String.fromCharCode(a[i]);
  }
  return s;
}
function RangeCoder() {
  this.base = 256;
  this.high = 1 << 24;
  this.low = 1 << 16;
  this.num = 256;
  this.values = [];
  this.inc = 8;

  this.reset = function() {
    this.values = [];
    for(var i = 0; i <= this.num; i++) {
      this.values.push(i);
    }
  };

  this.floordiv = function(a, b) {
    return Math.floor(a / b);
  };

  // Javascript numbers are doubles with 53 bits of integer precision so can
  // represent unsigned 32-bit ints, but logic operators like & and >> behave as
  // if on 32-bit signed integers (31-bit unsigned). Mask32 makes the result
  // positive again. Use e.g. after multiply to simulate unsigned 32-bit overflow.
  this.mask32 = function(a) {
    return ((a >> 1) & 0x7fffffff) * 2 + (a & 1);
  };

  this.update = function(symbol) {
    // too large denominator
    if(this.getTotal() + this.inc >= this.low) {
      var last = this.values[0];
      for(var i = 0; i < this.num; i++) {
        var d = this.values[i + 1] - last;
        d = (d > 1) ? this.floordiv(d, 2) : d;
        last = this.values[i + 1];
        this.values[i + 1] = this.values[i] + d;
      }
    }
    for(var i = symbol + 1; i < this.values.length; i++) {
      this.values[i] += this.inc;
    }
  };

  this.getProbability = function(symbol) {
    return [this.values[symbol], this.values[symbol + 1]];
  };

  this.getSymbol = function(scaled_value) {
    var symbol = this.binSearch(this.values, scaled_value);
    var p = this.getProbability(symbol);
    p.push(symbol);
    return p;
  };

  this.getTotal = function() {
    return this.values[this.values.length - 1];
  };

  // returns last index in values that contains entry that is <= value
  this.binSearch = function(values, value) {
    var high = values.length - 1, low = 0, result = 0;
    if(value > values[high]) return high;
    while(low <= high) {
      var mid = this.floordiv(low + high, 2);
      if(values[mid] >= value) {
        result = mid;
        high = mid - 1;
      } else {
        low = mid + 1;
      }
    }
    if(result > 0 && values[result] > value) result--;
    return result;
  };

  this.encodeString = function(text) {
    return arrayToString(this.encode(stringToArray(text)));
  };

  this.decodeString = function(text) {
    return arrayToString(this.decode(stringToArray(text)));
  };

  this.encode = function(data) {
    this.reset();

    var result = [1];
    var low = 0;
    var range = 0xffffffff;

    result.push(data.length & 255);
    result.push((data.length >> 8) & 255);
    result.push((data.length >> 16) & 255);
    result.push((data.length >> 24) & 255);

    for(var i = 0; i < data.length; i++) {
      var c = data[i];
      var p = this.getProbability(c);
      var total = this.getTotal();
      var start = p[0];
      var size = p[1] - p[0];
      this.update(c);
      range = this.floordiv(range, total);
      low = this.mask32(start * range + low);
      range = this.mask32(range * size);

      for(;;) {
        if(low == 0 && range == 0) {
          return null; // something went wrong, avoid hanging
        }
        if(this.mask32(low ^ (low + range)) >= this.high) {
          if(range >= this.low) break;
          range = this.mask32((-low) & (this.low - 1));
        }
        result.push((this.floordiv(low, this.high)) & (this.base - 1));
        range = this.mask32(range * this.base);
        low = this.mask32(low * this.base);
      }
    }

    for(var i = this.high; i > 0; i = this.floordiv(i, this.base)) {
      result.push(this.floordiv(low, this.high) & (this.base - 1));
      low = this.mask32(low * this.base);
    }

    if(result.length > data.length) {
      result = [0];
      for(var i = 0; i < data.length; i++) result[i + 1] = data[i];
    }

    return result;
  };

  this.decode = function(data) {
    if(data.length < 1) return null;
    var result = [];
    if(data[0] == 0) {
      for(var i = 1; i < data.length; i++) result[i - 1] = data[i];
      return result;
    }
    if(data[0] != 1) return null;
    if(data.length < 5) return null;

    this.reset();

    var code = 0;
    var low = 0;
    var range = 0xffffffff;
    var pos = 1;
    var symbolsize = data[pos++];
    symbolsize |= (data[pos++] << 8);
    symbolsize |= (data[pos++] << 16);
    symbolsize |= (data[pos++] << 24);
    symbolsize = this.mask32(symbolsize);

    for(var i = this.high; i > 0; i = this.floordiv(i, this.base)) {
      var d = pos >= data.length ? 0 : data[pos++];
      code = this.mask32(code * this.base + d);
    }
    for(var i = 0; i < symbolsize; i++) {
      var total = this.getTotal();
      var scaled_value = this.floordiv(code - low, (this.floordiv(range, total)));
      var p = this.getSymbol(scaled_value);
      var c = p[2];
      result.push(c);
      var start = p[0];
      var size = p[1] - p[0];
      this.update(c);

      range = this.floordiv(range, total);
      low = this.mask32(start * range + low);
      range = this.mask32(range * size);
      for(;;) {
        if(low == 0 && range == 0) {
          return null; // something went wrong, avoid hanging
        }
        if(this.mask32(low ^ (low + range)) >= this.high) {
          if(range >= this.low) break;
          range = this.mask32((-low) & (this.low - 1));
        }
        var d = pos >= data.length ? 0 : data[pos++];
        code = this.mask32(code * this.base + d);
        range = this.mask32(range * this.base);
        low = this.mask32(low * this.base);
      }
    }

    return result;
  };
}
function encodeBoard(text) {
  var lz77 = (new LZ77Coder()).encodeString(text);
  var range = (new RangeCoder()).encodeString(lz77);
  return '0' + toBase64(range); // '0' = format version
}
function toBase64(text) {
  var result = btoa(text);
  result = result.split('=')[0];
  result = result.replace(new RegExp('\\+', 'g'), '-');
  result = result.replace(new RegExp('/', 'g'), '_');
  return result;
}

let code = encodeBoard(`@input`);

let iframe = document.getElementById("logic_emu@0");

iframe.contentWindow.location.reload(true);

iframe.contentWindow.location.replace("https://liascript.github.io/logicemu_template/docs/index.html#code="+code);

//iframe.contentWindow.location.reload(true);

"LIA: stop";
</script>

<iframe id="logic_emu@0" width="100%" height="400px" src=""></iframe>

@end
-->

# Vortrag "Einführung in die technische Realisierung von Automaten"

**Samuel-von-Pufendorf-Gymnasiums, 1. Februar 2019**

Prof. Dr. Sebastian Zug, Technische Universität Bergakademie Freiberg

------------------------------

![Welcome](images/WorkingDesk.jpg "Experiments")<!-- width="80%" -->

## 1. Einführung

Studium der Angewandten Informatik an der Technischen Bergakademie Freiberg

![Welcome](images/AInfFreiberg.jpeg "Überblick")<!-- width="80%" -->

## 2. Motivation des Beispiels

Wieviel Informatik steckt in einer Ampel?

Vernetzung im Straßenverkehr, Koordination Verkehrsfluss

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
````
                   0       1        2       3       Zustand

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

### Zielstellung

<!--
style="width: 70%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
````
 EINGABEN                                  AUSGABEN

 Taktgeber            ╔═══════════╗
 ┴┴┴┴┴┴┴┴┴┴    2S  -->║           ║
 ┴───...──┴  100S  -->║   Ampel-  ║
                      ║           ║───┬──> Rot
                 .--->║           ║──┬┼──> Gelb
                 |.-->║ steuerung ║─┬┼┼──> Grün
                 ||.->║           ║ │││
                 |||  ╚═══════════╝ │││
                 ||'----------------╯││
                 |'------------------╯│
                 '--------------------╯
````

Wie setzen wir die Anwendung um?


## 3. Entwurf des Automaten

### Idee





### ... angewandt auf die Ampel
<!--
style="width: 80%; max-width: 460px; display: block; margin-left: auto; margin-right: auto;"
-->
````
                  .-- 2s --. .-- 2s --. .- 100s -.
                  |        | |        | |        |
                  |        v |        v |        v
                 .-.       .-.        .-.       .-.
 Ampelzustände  ( 0 )     ( 1 )      ( 2 )     ( 3 )
                 '-'       '-'        '-'       '-'
                  ^                              |
                  |                              |
                  .------------- 2s -------------.
````
Wie verhält sich unser System für verschiedenen Kombinationen der Variablen 2s und 100s?

    {{0-1}}
| 2_s | 100_s |  Zustand  | Zustand' |
|  0  |  0    |    0      |   0      |
|  0  |  0    |    1      |   1      |
|  0  |  0    |    2      |   2      |
|  0  |  0    |    3      |   3      |

    {{1-2}}
| 2_s | 100_s |  Zustand  | Zustand' |
|  0  |  0    |    0      |   0      |
|  0  |  0    |    1      |   1      |
|  0  |  0    |    2      |   2      |
|  0  |  0    |    3      |   3      |
|  0  |  1    |    0      |   0      |
|  0  |  1    |    1      |   1      |
| <span style="color:red"> 0 </span> |  <span style="color:red"> 1 </span>     |    <span style="color:red"> 3 </span>       |  <span style="color:red"> 3 </span>      |
|  0  |  1    |    3      |   3      |

    {{3}}
| 2_s | 100_s |  Zustand  | Zustand' |
|  0  |  0    |    0      |   0      |
|  0  |  0    |    1      |   1      |
|  0  |  0    |    2      |   2      |
|  0  |  0    |    3      |   3      |
|  0  |  1    |    0      |   0      |
|  0  |  1    |    1      |   1      |
|  0  |  1    |    2      |   3      |
|  0  |  1    |    3      |   3      |

    {{2-3}}
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
|  0  |  1    |   0   |   1  |   0   |   1  |
|  0  |  1    |   1   |   0  |   1   |   1  |
|  0  |  1    |   1   |   1  |   1   |   1  |
|  1  |  0    |   0   |   0  |   0   |   1  |
|  1  |  0    |   0   |   1  |   1   |   0  |
|  1  |  0    |   1   |   0  |   1   |   0  |
|  1  |  0    |   1   |   1  |   0   |   0  |

Wie kann man diese Wertetabellen minimieren?

```python
from sympy.logic import SOPform
from sympy import symbols

x3, x2, x1, x0 = symbols('2s 100s FF2 FF1')

FF1_minterms = [[0, 0, 0, 1],
                [0, 0, 1, 1],
                [0, 1, 0, 1],
                [0, 1, 1, 0],
                [0, 1, 1, 1],
                [1, 0, 0, 0],]
result = SOPform([x3, x2, x1, x0], FF1_minterms)
print "FF1 = " + str(result)

FF2_minterms = [[0, 0, 1, 0],
                [0, 0, 1, 1],
                [0, 1, 1, 0],
                [0, 1, 1, 1],
                [1, 0, 0, 1],
                [1, 0, 1, 0],]
result = SOPform([x3, x2, x1, x0], FF2_minterms)
print "FF2 = " + str(result)
```

Lösung
```
FF1 = (FF1 & ~2s) | (100s & FF2 & ~2s) | (2s & ~100s & ~FF1 & ~FF2)
FF2 = (FF2 & ~2s) | (FF2 & ~100s & ~FF1) | (2s & FF1 & ~100s & ~FF2)
```


## 4. Realsierung in der Simulation

Beispiel für Simulationsumgebung



Warum brauchen wir einen Takt?

```-ampel.asci

"2s 100s"          p"Clock"
  s s              *
  * *   *----------+----*  *-->O-->l0
  *-+-+-+-]a---->o-+->d-*--+-*---->l2
  * * * *-># *--># *  #    * *>O>a>l3
  * * * *    * *># **>c    *     ^
  *-+-+-+-]a-* *   *"FF1"  *-----*
  * *-+-+->#   *   *       *
  * * *-+->#   *   *       *
  * * * *      *   *       *
  *-+-+-+->a---*   *       *
  * *-+-+-]#       *       *
  * * *-+-]#       *       *
  * * * *-]#       *       *
  * * * *          *"FF2"  *
  *-+-+-+-]a---->o-+->d-*--*
  * * *-+-># *--># *  # *
  * * * *    * *># **>c *
  * *-+-+-]a-* *        *
  * * *-+->#   *        *
  * * * *-]#   *        *
  * * * *      *        *
  *-+-+-+->a---*        *
    *-+-+-]#            *
      *-+-]#            *
      * *->#            *
      *-----------------*
```
@logic_emu

## 5. Umsetzung auf dem Steckbrett

## 6. Zusammenfassung und Ausblick

__Ablauf beim Aufstellen eines Automaten__

1. Analyse des Systems, Identifikation von Eingängen, Ausgängen und Zuständen
2. Modellierung als Automat
3. Aufstellen der Wahrheitstafel
4. Ableiten der Schaltfunktionen
5. Realisieren des Schaltwerkes

__Mängel unserer Lösung__
* keine Berücksichtigung von gleichzeitig aktivem 2s und 100s
