Master-Leitfaden: Prompting für Stable Diffusion, Pony & Flux

Dieser Leitfaden dient als strukturierte Referenz für das Erstellen von Prompts über verschiedene Modell-Generationen hinweg – von den klassischen SD-Versionen bis hin zu den modernen Flux- und Spezial-Modellen.

1. Die Modell-Basen im Schnellüberblick

Bevor du ein Wort tippst, musst du wissen, welche Architektur unter der Haube steckt. Jede Generation hat ein anderes "Gehirn" (den Text-Encoder) und verarbeitet deine Eingaben grundlegend anders.

Architektur

Primärer Prompt-Stil

Negative Prompts?

Typische Auflösung

Hardware-Hunger

SD 1.5

Stichwort-Suppe (Tags)

Absolut Pflicht

$512 \times 512$ Pixel

Sehr niedrig

SDXL

Hybrid (Sätze + Tags)

Empfohlen

$1024 \times 1024$ Pixel

Mittel (mind. $8\text{ GB}$ VRAM)

Pony (SDXL-Spezial)

Spezifische Score-Tags

Optional / Minimal

$1024 \times 1024$ Pixel

Mittel (mind. $8\text{ GB}$ VRAM)

SD 3.5 / Flux

Natürliche Sprache (Roman)

Nein (ignoriert/verwirrt)

$1024 \times 1024$ Pixel+

Hoch bis Extrem

2. Die Master-Schablonen für Prompts

Schablone A: Die Tag-Struktur (Für SD 1.5 & Standard-SDXL)

Diese Modelle lesen keine natürlichen Sätze, sondern verarbeiten gewichtete Fragmente von links nach rechts. Was weiter vorne steht, erhält von der KI das stärkste Gewicht.

Warum funktioniert das so? (Das CLIP-Prinzip)

SD 1.5 und SDXL nutzen als "Übersetzer" sogenannte CLIP-Text-Encoder (entwickelt von OpenAI). CLIP funktioniert wie eine riesige Bilddatenbank mit Schlagworten (Tags).

CLIP versteht keine Grammatik oder logischen Beziehungen wie "Der Mann schaut auf das Pad, welches sein Gesicht beleuchtet".

Es sucht im Bild stattdessen einfach nach den Tags man, looking, pad, glowing, face.

Weil die KI die logische Beziehung nicht versteht, würfelt sie die Elemente oft durcheinander. Deshalb müssen wir die Tags strikt nach Wichtigkeit sortieren und unwichtige Füllwörter weglassen.

Struktur-Aufbau (Komma-getrennt)

Hauptmotiv (Wer oder was?): Das klare Zentrum des Bildes.

Beispiel: 1man, cyber detective, mechanical eye

Kleidung & physische Details: Was trägt das Motiv?

Beispiel: dark trench coat, glowing cybernetic implants

Umgebung & Hintergrund (Wo?): Die Kulisse definieren.

Beispiel: inside a dark wet alleyway, neon signs, rain, puddles

Kamera & Licht: Winkel, Brennweite und Ausleuchtung festlegen.

Beispiel: cinematic lighting, close-up shot, neon blue light illuminating his face

Stil- & Qualitäts-Tags: Stilistische Richtungsweiser.

Beispiel: photorealistic, gritty style, highly detailed

Der fertige Prompt:

1man, cyber detective, mechanical eye, dark trench coat, glowing cybernetic implants, inside a dark wet alleyway, neon signs, rain, puddles, cinematic lighting, close-up shot, neon blue light illuminating his face, photorealistic, gritty style, highly detailed

Wichtig – Der Negative Prompt:

Da das CLIP-Modell sehr leicht unsaubere Pfade im latenten Raum ansteuert (z. B. fehlerhafte Hände, weil es viele schlechte Fotos im Datensatz gab), musst du ihm explizit sagen, was es weglassen soll:

bad anatomy, deformed hands, extra limbs, blurry, mutation, drawing, illustration, painting, bright colors, cheerful

Schablone B: Die Roman-Struktur (Für Flux & SD 3.5)

Moderne Modelle nutzen gigantische Text-Encoder (wie T5). Sie verstehen echte Grammatik, Konjunktionen und Präpositionen (wie „hinter“, „neben“, „unter“).

Warum funktioniert das so? (Das T5-LLM-Prinzip)

Flux und SD 3.5 nutzen neben CLIP einen extrem mächtigen Sprachübersetzer namens T5-XXL (oder in Flux 2 das Mistral-Modell). Dies ist ein echter Sprach-Encoder, der auch in hochentwickelten Sprach-KIs (LLMs) steckt.

T5 liest deinen Prompt wie ein Mensch. Es versteht Konzepte wie Kausalität ("weil das Pad leuchtet, wird sein Gesicht erhellt").

Es kann komplexe Anweisungen pixelgenau zuordnen und versteht räumliche Beziehungen ("links neben dem großen Schild").

Der Nachteil von Tags: Wenn du hier eine "Stichwort-Suppe" wie 8k, masterpiece eingibst, versucht T5 diese Wörter logisch zu übersetzen. Die Folge: Die KI generiert oft physischen Text (z.B. das Wort "8k" als Graffiti an der Wand).

Struktur-Aufbau (Natürliche Sprache / Prose)

Schreibe einen flüssigen, beschreibenden Absatz. Erzähle der KI eine Szene so, als würdest du sie einem menschlichen Fotografen im Detail diktieren.

Der fertige Prompt:

A gritty, realistic close-up photo of a rugged cyber detective standing in a dark, rain-slicked alleyway at night. He is wearing a dark trench coat. In his hands, he holds a glowing blue holographic datapad, casting a vibrant cyan light onto his face. In the background, blurry neon signs reflect in the wet asphalt.

Wichtig:

Kein Negative Prompt nötig: T5 steuert das Modell so präzise an, dass es unerwünschte Stile von sich aus ignoriert. Negative Prompts verwirren den T5-Encoder meist nur.

C. Die Token-Grenze (Das $75$-Wort-Limit)

Ein extrem häufiger Anfängerfehler bei älteren Modellen betrifft die Länge des geschriebenen Texts.

Bei SD 1.5 und SDXL (Das CLIP-Limit):

Der CLIP-Text-Encoder schneidet deinen Prompt in sogenannte "Tokens" (Wortfragmente). CLIP hat ein hartes Limit von $75$ Tokens.

Was passiert bei längeren Prompts? Die meisten Web-UIs teilen den Prompt dann in mehrere Pakete auf ($75$, $150$, $225$...). Das Problem dabei ist: Wörter am Ende des ersten Pakets und Wörter im zweiten Paket verlieren massiv an Bedeutung und "übertragen" sich kaum noch auf das Bild.

Die Regel für unseren Detektiv: Halte den Prompt bei SD 1.5/SDXL so fokussiert und kurz wie möglich. Jedes unnötige Füllwort klaut einem wichtigen Tag (wie mechanical eye) die Aufmerksamkeit.

Bei Flux & SD 3.5 (Das T5-Limit):

Der T5-Encoder hat ein Limit von bis zu $512$ Tokens (einige Implementationen erlauben sogar noch mehr). Du kannst hier problemlos halbe Buchseiten einfügen. Das Modell liest den gesamten Text flüssig durch, ohne wichtige Details am Ende zu vergessen.

3. Sonderfall: Pony Diffusion (V6 & V7)

Pony-Modelle basieren zwar auf der SDXL- oder AuraFlow-Architektur, wurden aber völlig anders trainiert. Das Verständnis dafür, wie sie funktionieren, ist der Schlüssel zu perfekten Bildern.

Warum gibt es diese Tags überhaupt? (Das GIGO-Prinzip)

Wenn man eine KI trainiert, hat man folgendes Problem: Wenn man ihr nur perfekte Bilder füttert, lernt sie zu wenige Begriffe (weil es von manchen Nischen-Objekten oder Charakteren keine perfekten Bilder gibt). Füttert man sie mit Millionen unperfekter Bilder (Skizzen, Fan-Art, Foren-Uploads), wird sie "schlau", fängt aber an, schlechte Hände und hässliche Gesichter zu generieren.

Die Lösung von Pony: Die Entwickler haben die Trainingsbilder nach Qualität bewertet (von Note 1 bis Note 9). Jedes Bild im Gehirn der KI trägt also ein Qualitäts-Preisschild. Über die Prompts steuern wir, auf welche "Schublade" das Modell zugreifen darf.

+-------------------------------------------------------------+
|                     DAS TRAININGSDATEN-ARCHIV                |
|                                                             |
|  [Schublade score_9]   --> Nur perfekte Meisterwerke        |
|  [Schublade score_8]   --> Sehr gute, detailreiche Bilder  |
|  [Schublade score_7]   --> Akzeptable, normale Zeichnungen  |
|  [Schublade score_4-5] --> Skizzen, Gekritzel, Amateur-Art  |
+-------------------------------------------------------------+


Wenn du deine Qualitäts-Tags weglässt, greift die KI auf den gesamten Topf zu. Das Bild wird instabil. Setzt du die Tags davor, zwingst du das Modell, das Motiv im Stil der hochwertigsten Schubladen zu zeichnen.

Warum prompten wir nicht einfach NUR "score_9"?

Es ist der logischste Gedanke überhaupt: Wenn score_9 für die absolut fehlerfreien Meisterwerke steht, warum tippen wir dann nicht einfach nur dieses eine Wort? Warum tun wir uns den Stress mit der langen Zahlenkette an?

Dafür gibt es zwei Hauptgründe:

1. Der "Ausbrenn"-Effekt (Overfitting / Vielfalts-Kollaps)

Die Anzahl der absolut makellosen, perfekten Bilder im Internet, die eine 9 verdient haben, ist extrem klein.
Wenn du der KI befiehlst: "Zeige mir ein Bild und greife NUR auf den Topf score_9 zu", schränkst du das Vokabular der KI massiv ein. Sie kennt in dieser Schublade vielleicht nur drei Gesichter, zwei Posen und einen Zeichenstil.

Die Folge: Deine Bilder sehen alle identisch aus (Overfitting). Die Gesichter werden starr, die Posen extrem langweilig, und die KI verliert jegliche Kreativität.

Die Lösung: Durch die Kette (score_8_up, score_7_up etc.) erlaubst du der KI, auf Millionen weiterer Bilder zuzugreifen, um Posen, Kleidung und Hintergründe abzuwandeln – während sie die Sauberkeit von score_9 beibehält.

2. Der "Brücken"-Effekt (Wie man seltene Dinge rettet)

Stell dir vor, du möchtest ein sehr seltenes Motiv generieren – zum Beispiel eine "historische Schreibmaschine aus dem Jahr 1920".

In der perfekten score_9-Schublade existiert dieses Objekt überhaupt nicht, weil kein Profi-Künstler ein Meisterwerk einer solchen Schreibmaschine gemalt hat.

In den schlechteren Schubladen (score_5 oder score_4) gibt es jedoch 20 eingescannte Fotos oder Skizzen von dieser Schreibmaschine.

Wenn du jetzt nur score_9 promptest, weiß die KI nicht, was eine Schreibmaschine ist, und ignoriert deinen Befehl.

Promptest du die Kette bis score_4_up, sagst du der KI: "Hole dir das Wissen, wie diese Schreibmaschine aussieht, aus den schlechteren Töpfen. Aber zeichne sie mir so sauber und fehlerfrei wie die Bilder aus dem 9er-Topf!"

Welcher Wert zählt am Ende wirklich?

Wenn wir eine Kette wie score_9, score_8_up, score_7_up eingeben, welcher Wert setzt sich dann durch?

Die Antwort ist: Sie arbeiten zusammen, aber mit einer klaren Aufgabenverteilung.

Der Stil & die Rendering-Qualität (Wer bestimmt das Aussehen?):

Hier gewinnt immer der höchste Wert (score_9 und score_8_up). Die KI nutzt diese Töpfe als "Stil-Filter". Sie bestimmt, wie fein die Linien gezogen werden, wie sauber die Schattierungen sind und wie fehlerfrei die Gesichter und Hände gerendert werden. Dein fertiges Bild wird also wie ein score_9-Bild aussehen.

Die Objekterkennung & Komposition (Wer bestimmt den Inhalt?):

Hier gewinnen die niedrigeren Werte (z.B. score_6_up oder score_5_up). Sie öffnen die Datenbanken für komplexere Posen, Hintergründe und selteneres Vokabular.

Zusammenfassend:

Die hohen Scores bestimmen das WIE (die Qualität und den Stil), während die niedrigeren Scores das WAS bestimmen (welche Objekte und Details die KI überhaupt kennt). Zusammen bilden sie das perfekte Team.

A. Die Qualitäts-Zahlen (Score-Tags in V6)

Aufgrund eines Fehlers im Trainingsprozess von Pony V6 hat sich eine exakte Kette als optimal erwiesen, um die "Meisterwerk-Schubladen" zu öffnen.

Setze diese Kette immer ganz an den Anfang deines positiven Prompts:

Pflicht-Präfix V6: score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up

💡 Exkurs: Warum brauche ich die GANZE Kette und nicht nur "score_9"? (Der Token-Bug)

Neben dem Brücken-Prinzip gibt es bei Pony V6 einen berühmten technischen Bug:

In der Trainingsphase von Pony V6 ist dem Entwickler ein Missgeschick unterlaufen. Die KI hat die gesamte Kette score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up nicht als sechs einzelne Befehle gelernt, sondern als einziges, langes zusammenhängendes Wort (Token) abgespeichert.
Wenn du nur score_9 eingibst, "versteht" die KI das zwar, aber der Effekt ist extrem schwach, weil du nicht den genauen Schlüssel benutzt, der während des Trainings in das Gehirn der KI eingebrannt wurde.

B. Die Quell-Zugehörigkeit (Source-Tags)

Du musst dem Modell sagen, aus welchem Medium der Stil gezogen werden soll. Pony wurde auf unterschiedlichen Ästhetiken trainiert. Setze diesen Tag direkt nach den Score-Tags:

source_anime $\rightarrow$ Erzwingt den typischen 2D-Animations/Anime-Look.

source_cartoon $\rightarrow$ Westlicher Comic- und Zeichentrickstil.

source_furry $\rightarrow$ Für anthropomorphe (tierähnliche) Charaktere.

source_pony $\rightarrow$ Klassischer Pony-Stil (My Little Pony).

C. Altersfreigabe (Safety Ratings)

Pony trennt SFW (jugendfrei) und NSFW (nicht jugendfrei) strikt über eingebaute Jugendschutz-Tags. Wenn du diese nicht setzt, driftet das Modell oft in anzügliche Darstellungen ab:

rating_safe $\rightarrow$ Absolut jugendfrei (Pflicht für normale Bilder).

rating_questionable $\rightarrow$ Leicht anzüglich / Pin-up / Ecchi.

rating_explicit $\rightarrow$ Vollwertige NSFW-Generierungen.

D. Pony V7 Spezial: Die Stil-Cluster

Pony V7 (basiert auf AuraFlow) geht noch einen Schritt weiter. Weil die einfachen "Score"-Tags in V7 an Wirkung verloren haben, führte man das Konzept der Style Clusters ein. Die KI hat während des Trainings gelernt, Bilder nach Stil-Gruppen zu sortieren. Diese rufen wir über exakte IDs auf:

style_cluster_1324 $\rightarrow$ Der 2D-Meister: Erzwingt einen extrem sauberen, klassischen flachen 2D-Anime-Stil.

style_cluster_1679 $\rightarrow$ Der 3D-Realist: Biegt das Bild extrem stark in Richtung semi-realistisch, 3D-Render oder sogar lebensechtes Foto.

Der fertige Pony V6 Prompt (Beispiel Cyber-Detektiv):

score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, source_anime, rating_safe, 1boy, solo, cyber detective, mechanical eye, dark trench coat, holding glowing blue holographic datapad, standing in dark rainy alley, neon light reflections on wet street

Der fertige Pony V7 Prompt (Beispiel Cyber-Detektiv im Semi-Realismus):

style_cluster_1679, rating_safe, 1boy, solo, cyber detective, mechanical eye, dark trench coat, holding glowing blue holographic datapad, standing in dark rainy alley, neon light reflections on wet street, sharp photorealistic details

4. Fortgeschrittene Techniken (Advanced Spickzettel)

A. Inpainting (Bereiche gezielt reparieren)

Wenn das Bild großartig ist, aber Details wie Hände, Gesichter oder Objekte Fehler aufweisen.

Die Maske: Du malst den fehlerhaften Bereich im Web-UI mit dem Pinsel-Werkzeug aus.

Die Prompt-Regel: Beschreibe nur das, was innerhalb der Maske neu entstehen soll. Wiederhole nicht den gesamten Prompt.

Falsch: Der komplette original Prompt des Bildes, obwohl du nur das Hologramm korrigierst.

Richtig: a hand holding a glowing blue holographic datapad, detailed skin texture

Wichtige Einstellung: Setze im UI die Option Inpaint area auf "Only Masked". Dadurch konzentriert das Modell seine volle Rechenleistung und Auflösung ausschließlich auf den maskierten Ausschnitt.

B. Outpainting (Bildgrenzen erweitern)

Vergrößert ein Bild (z.B. von einem quadratischen Format $1:1$ auf ein Breitbild-Format $16:9$).

Die Prompt-Regel: Beschreibe vor allem die neue Umgebung, die an den Rändern hinzukommen soll. Erwähne das Hauptmotiv nur noch minimal, damit die KI es nicht versehentlich ein zweites Mal in die erweiterten Ränder generiert.

Beispiel für unseren Detektiv: dark rain-slicked city streets, towering sci-fi skyscrapers with glowing windows in the far background, reflections of neon signs on puddles, depth of field

Denoising Strength: Halte diesen Wert beim Outpainting relativ hoch (zwischen $0.6$ und $0.8$), damit das Modell genügend kreativen Spielraum hat, um den leeren Raum nahtlos und passend weiterzudenken.

C. ControlNet (Präzise Struktur- und Posensteuerung)

Zusatznetzwerke, die der KI eine feste Geometrie aufzwingen. Der Prompt steuert dann nur noch Texturen und Stile, nicht mehr die Komposition.

ControlNet-Modell

Funktionsweise

Prompt-Empfehlung

OpenPose

Liest das menschliche Skelett aus und zwingt die KI in diese Pose.

Beschreibe Kleidung, Licht und Gesichtsausdruck des Detektivs. Ignoriere Verben zur Körperhaltung (z.B. "stehend"), da das Skelett dies bereits definiert.

Canny / Lineart

Erstellt eine präzise Strichzeichnung aller Kanten eines Referenzbildes.

Ideal für das Gehäuse des Datapads oder des mechanischen Auges. Der Prompt beschreibt primär Materialien, Farben, Oberflächen und den Hintergrund.

Depth

Generiert eine 3D-Tiefenkarte (Vorder- und Hintergrund).

Perfekt für die Gasse, um die räumliche Tiefe und die exakten Größenverhältnisse der Wände und des Detektivs beizubehalten.

D. Prompt-Gewichtung (Nur für SD 1.5 & SDXL)

Wenn ein Element im Bild untergeht, kannst du dessen Gewichtung manuell anpassen:

Verstärken: (holographic datapad:1.2) $\rightarrow$ Erhöht die Priorität um $20\%$.

Abschwächen: (holographic datapad:0.8) $\rightarrow$ Reduziert die Priorität um $20\%$.

Achtung: Nutze keine Werte über $1.4$, da dies zu Farbfehlern und Bildartefakten führt. Bei modernen Modellen wie Flux haben mathematische Klammer-Gewichtungen keine Funktion und sollten weggelassen werden.

E. Wildcards (Automatisierte Prompt-Variationen)

Wenn du viele Bilder testen möchtest, ohne jeden Prompt einzeln zu schreiben. Wildcards sind Textdateien voller Alternativen, die das UI im Zufallsprinzip abruft.

Die Syntax: Du nutzt geschweifte Klammern und vertikale Striche im Prompt für direkte "Inline-Auswahl" oder Verweise auf Textdateien via __dateiname__.

Beispiel für unseren Detektiv:

Statt stur eine Lederjacke zu rendern, lassen wir das UI rotieren:

1man, cyber detective, wearing a {dark trench coat|brown leather jacket|rugged tactical vest}, holding a glowing blue holographic datapad...
Das System generiert bei $10$ Bildern automatisch eine Mischung aus Detektiven in Mänteln, Lederjacken und Westen.

Nutzen: Perfekt für Massen-Generierungen (Batches), um den Sweet Spot für Kleidung, Hintergründe oder Lichtstimmungen ({neon blue|cyberpunk purple|toxic green}) herauszufinden.

F. Regional Prompting (Bereichsbezogenes Prompting)

Verhindert "Prompt-Bleeding" – das Phänomen, dass z. B. das helle Blau des Hologramms versehentlich auch die schwarze Jacke oder die gesamte Gasse blau färbt.

Die Funktionsweise: Du teilst den Canvas im UI (über Extensions wie Regional Prompter in Forge/A1111 oder über Attention Masking/Conditioning Nodes in ComfyUI) in geometrische Regionen auf (z. B. Spalten oder Masken-Zonen).

Der Prompt-Aufbau (Spalten-Beispiel: Links, Mitte, Rechts):

Globale Ebene (Ganze Szene): A cinematic photo inside a wet cyberpunk alleyway at night

ADD COL (Spalte 1 - Links): towering sci-fi skyscraper, flickering red neon sign

ADD COL (Spalte 2 - Mitte): a rugged cyber detective wearing a matte-black leather jacket, holding a glowing blue datapad

ADD COL (Spalte 3 - Rechts): a warm glowing street food stall, steam rising, retro-futuristic noodle bar

Nutzen: Die Farben und Objekte bleiben streng in ihren Regionen getrennt. Das Blau des Datapads in der Mitte blutet nicht in das Rot des linken Schildes oder das Orange der rechten Nudelbar.

5. Das Praxis-Experiment: Ein Motiv, alle Modelle

Um den Unterschied im Prompting-Verhalten der verschiedenen Architekturen zu veranschaulichen, übersetzen wir eine einzige Bild-Idee in die exakte Sprache des jeweiligen Modells.

Die Kern-Idee (Das gewünschte Bild)

Szene: Ein cooler, kybernetischer Detektiv, der in einer dunklen, regennassen Gasse steht. Er hält ein leuchtendes, blaues Hologramm-Datenpad in den Händen, dessen Schein sein Gesicht beleuchtet. Im Hintergrund reflektieren Neon-Schilder auf dem nassen Asphalt.

A. Für SD 1.5 (Die Stichwort-Suppe)

Die Prompt-Logik: Keine Sätze. Reine Fragmente, absteigend nach Wichtigkeit sortiert. Am Ende stehen künstliche Qualitäts-Keywords, um die alte Engine zu schärfen.

Positiver Prompt:

1man, cyber detective, holding glowing blue holographic datapad, cyberpunk style, dark rainy alleyway, wet streets, neon reflections, cinematic lighting, photorealistic, masterpiece, highly detailed, sharp focus, 8k resolution, award winning photography


Negativer Prompt:

bad anatomy, deformed hands, extra fingers, blurry, drawing, illustration, painting, bright colors, cheerful, ugly, low resolution


B. Für SDXL (Der Hybrid-Stil)

Die Prompt-Logik: Kurze Sätze gemischt mit beschreibenden Details. Die Engine versteht Kompositionen bereits viel besser. Qualitäts-Tags wie "8k" fallen weg.

Positiver Prompt:

A cinematic, photorealistic shot of a rugged cyber-detective standing in a dark, rainy alleyway. He is holding a glowing holographic datapad that casts neon blue light onto his face. Wet asphalt with colorful neon reflections, high-tech details, 35mm photograph.


Negativer Prompt:

3d render, anime, cartoon, bad anatomy, deformed hands, blurry, low contrast


C. Für Pony V6 (Der Anime-Code)

Die Prompt-Logik: Die V6-Qualitätskette muss zwingend davor stehen. Es wird die Quell-Engine source_anime definiert. Sätze werden weitgehend vermieden und durch Danbooru-Tags ersetzt.

Positiver Prompt:

score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up, source_anime, rating_safe, 1boy, solo, cyber detective, holding glowing holographic datapad, standing in dark rainy alley, neon lights reflection, cyberpunk style, cinematic atmosphere


Negativer Prompt:

score_3_up, score_2_up, score_1_up, rating_explicit, rating_questionable, bad anatomy, deformed hands, extra limbs, blurry


D. Für Pony V7 (Der 3D/CGI-König)

Die Prompt-Logik: Wir nutzen kein V6-Satzfragment mehr, sondern aktivieren den Stil-Cluster style_cluster_1679 für die 3D/semi-realistische Plastizität.

Positiver Prompt:

style_cluster_1679, rating_safe, 1boy, solo, cyber detective, cyberpunk, holding glowing blue datapad, standing in dark rainy alleyway, neon light reflections on wet ground, highly detailed skin texture, cinematic lighting


Negativer Prompt:

style_cluster_1324, rating_explicit, rating_questionable, bad anatomy, deformed hands, blurry


E. Für Flux.1 / Flux 2 & SD 3.5 (Die pure Roman-Struktur)

Die Prompt-Logik: Absolut natürliche Sprache. Beschreibe die Szene so, als würdest du sie einem Menschen am Telefon erklären. Das Modell kapiert die Logik ("das Licht, das auf sein Gesicht fällt") fehlerfrei.

Positiver Prompt:

A gritty, highly realistic photo of a rugged cyber-detective standing in a dark, rain-slicked alleyway at night. The alley is lit by flickering purple and blue neon signs. The detective is looking down at a glowing holographic datapad he is holding in his hands, which casts a bright cyan glow onto his face. Water drops are visible on his leather jacket, and the reflections on the wet asphalt are sharp and detailed.


Negativer Prompt:

(Komplett leer lassen)




6. Zusatznetzwerke: LoRAs & Embeddings

Zusatzdateien erlauben es dir, Stile, Charaktere, Posen oder bestimmte Kleidungsstücke pixelgenau zu steuern, ohne ein komplett neues Basis-Modell herunterladen zu müssen.

A. LoRA (Low-Rank Adaptation)

Ein LoRA ist wie ein "Aufsatz-Plugin" für das Gehirn der KI. Es verändert nur einen winzigen Prozentsatz der Gewichte des Basis-Modells, um ein extrem spezifisches Konzept zu erzwingen.

Die große UI-Falle: Muss das <lora:...>-Tag überhaupt in den Prompt?

Das ist einer der häufigsten Fehler! Ob du einen LoRA-Befehl aktiv in deinen Prompt schreiben musst, hängt ausschließlich von deiner Benutzeroberfläche (UI) ab:

In Automatic1111, WebUI-Forge und SD-Next:

JA. Hier musst du das LoRA über eine spezielle Syntax direkt im Text-Prompt aufrufen.

Syntax: <lora:LoRA-Dateiname:Stärke>

Beispiel: <lora:CyberArmor_v1:0.8> (Lädt das LoRA mit einer Stärke von $80\%$).

In ComfyUI:

NEIN! Wenn du hier <lora:...> in deinen Text-Node tippst, ignoriert die KI das komplett oder versucht verzweifelt, den Text "lora" zu zeichnen. In ComfyUI werden LoRAs über physische Nodes (Lade-Blöcke) direkt in den Modell-Pfad (Model & CLIP) eingeklinkt, bevor der Text-Encoder überhaupt ins Spiel kommt. Dein Prompt bleibt also sauber!

In Fooocus, Draw Things oder Web-Generatoren (wie Civitai):

NEIN. Hier wählst du LoRAs über separate Menüs, Checkboxen oder Schieberegler aus. Der eigentliche Prompt-Kasten bleibt frei von technischem Code.

Das universelle Gesetz der Trigger-Words (Aktivierungswörter)

Unabhängig davon, wie dein UI das LoRA lädt: Wenn das LoRA mit bestimmten Aktivierungswörtern trainiert wurde, musst du diese Wörter zwingend in deinen Prompt einbauen. Andernfalls ist das LoRA zwar geladen, weiß aber nicht, wann und worauf es seine Gewichte anwenden soll.

Beispiel für unseren Cyber-Detektiv (SDXL in Automatic1111):

Wenn wir ihm einen ganz bestimmten "Cyberpunk-Tech-Rüstungs-Look" verpassen wollen, nutzen wir ein LoRA namens CyberArmor mit dem Trigger-Word cyberarmor-style:

A cinematic shot of a rugged cyber-detective standing in a dark, rainy alleyway, wearing <lora:CyberArmor_v1:0.8> cyberarmor-style mechanical plate-armor, holding a glowing holographic datapad...

(Hier ist <lora:...:0.8> der technische Lade-Befehl für Automatic1111 und cyberarmor-style das inhaltliche Trigger-Word, das die Rüstung im Bild tatsächlich entstehen lässt).

B. Embeddings / Textual Inversion

Ein Embedding ist kein eigenständiges Netzwerk, sondern eine Art "Vokabel-Abkürzung". Stell dir vor, du trainierst der KI ein neues Wort für ein bestimmtes Gesicht ein. Statt "schmale Nase, blaue Augen, Sommersprossen, runde Brille" schreibst du einfach das Wort MyCustomFace in den Prompt.

Der Haupt-Einsatzzweck heute: Negative Embeddings. Weil man bei SD 1.5 und SDXL extrem viele fehlerhafte Körperteile ausfiltern muss, hat die Community gigantische Negativ-Vokabeln gebaut (z.B. easynegative, bad-hands-5, FastNegative).

Die Anwendung: Du legst die Datei in den embeddings-Ordner deiner UI und tippst den Namen einfach in den Negative Prompt.

Embedding-Beispiel für unseren Detektiv (SD 1.5):

Positiver Prompt: 1man, cyber detective, holding glowing blue holographic datapad...

Negativer Prompt: bad anatomy, extra limbs, bad-hands-5, easynegative
(Das Embedding bad-hands-5 filtert im Hintergrund hunderte anatomische Fehler heraus).

7. Die wichtigsten Stellschrauben (Settings)

Ein genialer Prompt bringt nichts, wenn die mathematischen Einstellungen im Generator-UI nicht zur Architektur passen.

A. CFG Scale (Classifier-Free Guidance)

Die CFG Scale ist der "Striktheits-Regler" für die KI. Sie bestimmt, wie sklavisch sich das Modell an deinen Prompt hält (hoher Wert) oder wie viel kreativen Freiraum es hat (niedriger Wert).

SD 1.5 & SDXL:

Süßer Punkt (Sweet Spot): $5.0$ bis $8.0$.

Was passiert bei Extremen? Unter $4.0$ wird das Bild oft verwaschen und ungenau. Über $12.0$ brennt das Bild förmlich aus ("burnt look") – die Farben werden extrem übersättigt und es entstehen hässliche Pixel-Artefakte.

Flux (Sonderfall "Distilled Guidance"):

Flux-Modelle sind größtenteils "distilled". Das bedeutet, die CFG-Berechnung ist fest im Modell verankert.

CFG Scale: Muss auf $1.0$ stehen! (Klassisches CFG ist hier deaktiviert).

Guidance Scale (separater Regler): Steht idealerweise auf $3.5$ bis $4.0$ (für Flux Dev/Flex). Flux Schnell braucht gar keine Guidance (auf $1.0$ oder $0.0$ lassen).

B. Sampling Steps (Schritte)

Wie oft das Bild aus dem anfänglichen statischen Rauschen (Noise) "herausgerechnet" wird.

SD 1.5 / SDXL: $20$ bis $35$ Schritte. Mehr Schritte bringen ab einem gewissen Punkt (meist ab $40$) keine Qualitätssteigerung mehr, sondern kosten nur noch Rechenzeit.

Flux Dev / Flux 2 Flex: $20$ bis $30$ Schritte sind optimal für maximale Schärfe.

Flux Schnell (Schnell-Modelle): $4$ bis $8$ Schritte reichen völlig aus, da das Modell extrem darauf optimiert wurde, in Rekordzeit Bilder zu erstellen. Mehr Schritte zerstören das Bild hier sogar.

C. Sampler & Schedulers

Die mathematische Methode, wie das Rauschen Schritt für Schritt entfernt wird.

Für den realistischen "Foto"-Look (SD 1.5 & SDXL):

DPM++ 2M Karras oder DPM++ SDE Karras: Liefern extrem weiche, fotorealistische Hautstrukturen und fehlerfreie Lichtverläufe in den nassen Gassen unseres Detektivs.

Für Anime & scharfe Linien (Pony):

Euler a oder DPM++ 2M Karras. Euler-Sampler neigen dazu, die flachen Farbflächen bei 2D-Zeichnungen sauberer zu halten.

Für Flux:

Euler mit dem Scheduler Simple oder Beta ist hier der absolute Standard. Flux regelt die Plastizität und Schärfe direkt im Transformer, weshalb komplexe Sampler wie DPM++ hier meistens gar nicht nötig sind.

D. Auflösung, Bildformat & Hi-Res Fix (Die Doppelkopf-Falle)

Das gewählte Bildformat entscheidet massiv darüber, wie stabil die Geometrie deines Bildes bleibt.

Das Problem bei SD 1.5 & SDXL:
Diese Modelle wurden nativ auf quadratischen Formaten trainiert ($512 \times 512$ bzw. $1024 \times 1024$ Pixel). Wenn du im UI direkt eine Auflösung wie $1024 \times 576$ (ein weites $16:9$-Format) bei SD 1.5 einstellst, bricht die Logik des Modells zusammen.

Die Folge: Weil das Modell die Gasse "breiter" malen muss, als es gelernt hat, fängt es an, das Motiv zu spiegeln. Du bekommst plötzlich zwei Detektive im Bild, die sich die Hände halten, oder Menschen mit deformierten Doppelköpfen.

Die Lösung (Hi-Res Fix): Generiere das Bild immer zuerst in der nativen Auflösung ($512 \times 512$ für SD 1.5) und aktiviere im UI den Hi-Res Fix (High-Resolution Fix). Dieser skaliert das fertige Bild im zweiten Durchgang hoch und füllt die Ränder stabil mit Details, ohne die Anatomie zu zerreißen. Setze die Denoising Strength im Hi-Res-Fix-Menü auf einen Wert zwischen $0.3$ und $0.5$.

Die Stärke von Flux:
Flux wurde mit einer Technik namens Resolution Bucketing auf unzähligen verschiedenen Seitenverhältnissen gleichzeitig trainiert. Du kannst hier völlig problemlos direkt ein superweites Breitbild (z. B. $1456 \times 816$ Pixel) oder ein extremes Hochformat einstellen. Flux passt die Positionierung des Detektivs und die Komposition der Gasse automatisch und vollkommen fehlerfrei an das Format an. Ein "Hi-Res Fix" ist hier für die reine Bildstabilität nicht mehr notwendig.

8. Der Profi-Workflow: Iterative Bildentwicklung & Charakter-Konsistenz

Wenn du professionell mit Stable Diffusion oder Flux arbeitest, erstellst du Bilder nicht in einem einzigen "Zufallswurf". Du baust sie schrittweise auf. Hier ist der präzise 3-Phasen-Workflow, um Fehler zu korrigieren und denselben Charakter in völlig neue Szenen zu versetzen.

+-------------------------------------------------------------+
| 1. TEXT-TO-IMAGE     --> Der Detektiv entsteht (Alleyway)   |
|         |                                                   |
| 2. DETAIL-FIXING     --> ADetailer / FaceDetailer schärfen  |
|         |                die Augen, Hände und das Gesicht.  |
|         v                                                   |
| 3. SCENE TRANSFER    --> Multi-Reference / IP-Adapter packt |
|                          den Detektiv in eine neue Szene.   |
+-------------------------------------------------------------+


Phase 1: Die Initial-Generierung (Der "Rohentwurf")

Du nimmst den passenden Prompt aus Kapitel 5 (z.B. für Flux oder SDXL) und generierst dein erstes Bild. Der Detektiv steht in der dunklen Gasse.

Phase 2: Die automatische Gesicht- und Augenkorrektur (Detail-Fixing)

Oft sind bei Ganzkörper-Aufnahmen oder detailreichen Szenen die Augen des Charakters asymmetrisch oder das Gesicht wirkt verwaschen. Statt mühsam manuell inpainting zu betreiben, nutzt man automatische Werkzeuge direkt beim Generieren:

In Automatic1111 / WebUI-Forge: Aktiviere das Plugin ADetailer (Active Detailer).

In ComfyUI: Nutze die Node FaceDetailer (aus dem Impact-Pack).

Wie funktioniert das?

Ein integriertes Erkennungsmodell (meist ein YOLO-Objektdetektor) sucht im frisch berechneten Bild vollautomatisch nach Gesichtern (face_yolov8n.pt) und Augen (hand_yolov8n.pt).

Es schneidet das Gesicht maskenartig im Hintergrund aus.

Es jagt dieses Gesicht mit einem eigenen Mini-Inpainting-Durchlauf (Denoising-Stärke idealerweise auf $0.3$ bis $0.45$) noch einmal durch das neuronale Netz.

Der Prompt-Trick: Du kannst im ADetailer-Menü einen separaten Prompt eintragen, der nur auf das Gesicht angewendet wird.

Beispiel für den Detektiv: close-up of a handsome rugged face, glowing blue mechanical eye, extremely detailed skin texture

Das fertig berechnete, gestochen scharfe Gesicht wird nahtlos zurück in das Originalbild eingefügt. Deine Augen und Gesichter sind ab jetzt immer perfekt.

Phase 3: Der Szenenwechsel bei gleichem Charakter (Identity Locking)

Jetzt hast du das perfekte Bild deines kybernetischen Detektivs. Nun möchtest du ein zweites Bild generieren: Derselbe Detektiv soll in einer hell erleuchteten, retro-futuristischen Nudelbar sitzen und eine Schüssel heiße Ramen essen.

Wie verhinderst du, dass die KI ein komplett neues Gesicht zeichnet?

Methode A: Native Multi-Reference (Mit Flux 2 oder Flux Kontext)

Moderne Architekturen wie Flux 2 unterstützen das direkte Einspeisen von Referenzbildern, ohne dass du ein LoRA trainieren musst.

Lade dein Bild aus Phase 1 in den dafür vorgesehenen Referenz-Slot (z.B. in LTX Studio oder entsprechende ComfyUI-Workflows).

Schreibe einen präzisen, beschreibenden Prompt, der sich direkt auf die Bild-Referenz bezieht.

Der Prompt-Aufbau:

The rugged cyber detective from image 1 is sitting inside a bright, neon-lit retro-futuristic noodle bar. He is holding a pair of chopsticks and eating from a bowl of steaming hot ramen. He still wears his dark trench coat, but it is now unbuttoned. The warm orange light from the kitchen illuminates his face with its glowing blue cybernetic eye.

Methode B: IP-Adapter & PuLID (Mit SDXL / Flux Dev)

Wenn du ein lokales ComfyUI- oder WebUI-Forge-Setup nutzt, sind Zusatznetzwerke wie IP-Adapter (Image Prompt Adapter) oder PuLID (Pure Light ID) der absolute Goldstandard.

IP-Adapter/PuLID Node aktivieren: Du lädst das Bild deines Detektivs in eine spezielle "Reference Image" Node.

Die Magie: Das Zusatznetzwerk extrahiert die mathematischen Gesichts-Merkmale (Biometrie) des Detektivs und speist sie direkt in das Gehirn der KI ein, während diese das neue Bild berechnet.

Dein Text-Prompt: Beschreibt einfach nur die neue Szene: A close-up shot of a rugged man eating ramen in a neon-lit futuristic diner...

IP-Adapter sorgt dafür, dass das Gesicht des Mannes exakt so aussieht wie das deines Detektivs, obwohl er in einer völlig anderen Umgebung sitzt.

Methode C: Der ReActor-Face-Swap (Der brute-force Weg)

Wenn alles andere fehlschlägt und du $100\%$-ige Gesichtsübereinstimmung erzwingen willst:

Generiere die neue Szene (Detektiv beim Ramen-Essen) ganz normal über Text.

Nutze das Tool ReActor (basiert auf InsightFace) in deinem UI.

Lade das Originalgesicht aus Phase 1 als "Source" und das neue Bild als "Target".

ReActor schneidet das Gesicht aus dem ersten Bild aus, berechnet den Winkel, die Schatten sowie das Licht der neuen Nudelbar und pflanzt die Gesichtszüge perfekt auf den neuen Körper.
