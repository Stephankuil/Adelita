import sqlite3
import pandas as pd
import csv
import json
# SQL-scripts
sql_script_1 = """
-- Tabel voor planten
CREATE TABLE IF NOT EXISTS planten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
    botanische_naam TEXT,
    beschrijving TEXT,
    te_gebruiken_bij TEXT,
    gebruikt_plantendeel TEXT,
    aanbevolen_combinaties TEXT,
    niet_te_gebruiken_bij TEXT,
    categorie_kleur TEXT,
    details TEXT,
    afbeelding TEXT
);

-- Tabel voor klachten
CREATE TABLE IF NOT EXISTS klachten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
    beschrijving TEXT
);

-- Tussentabel voor relatie tussen planten en klachten
CREATE TABLE IF NOT EXISTS plant_klacht (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    klacht_id INTEGER NOT NULL,
    FOREIGN KEY (plant_id) REFERENCES planten(id),
    FOREIGN KEY (klacht_id) REFERENCES klachten(id)
);

-- Voeg planten toe
INSERT INTO planten (naam) VALUES 
('Acidophilus'),
('Aloe Vera'),
('Artisjok'),
('Ashwagandha'),
('Avena Sativa'),
('Bacopa'),
('Biergist'),
('Blauwe Bosbesvrucht'),
('Borage-olie'),
('Boswellia'),
('Brandnetel'),
('Canadese Geelwortel'),
('Cat’s Claw'),
('Cranberry'),
('Curcuma'),
('Damiana'),
('Driekleurig Viooltje'),
('Duivelsklauw'),
('Echinacea'),
('Fenegriek'),
('Garcinia'),
('Gember'),
('Ginkgo'),
('Ginseng'),
('Goudpapaver'),
('Griffonia'),
('Groene Thee'),
('Grote Klis'),
('Guarana'),
('Heermoes'),
('Hop'),
('Javaanse Thee'),
('Kersensteel'),
('Konjac'),
('Laksavital'),
('Levertraanolie'),
('Lijnzaadolie'),
('Lithothamnium'),
('Maca'),
('Maretak'),
('Mariadistel'),
('Maté'),
('Meidoorn'),
('Melisse'),
('Moederkruid'),
('Paardenbloem'),
('Passiebloem'),
('Plantaardige Kool'),
('Pompoenpitolie'),
('Propolis'),
('Q10'),
('Reishi – Shiitake – Maitake'),
('Resveratrol'),
('Rhodiola'),
('Rode Gist Rijst'),
('Rode Klaver'),
('Royal Jelly'),
('Russische Ginseng'),
('Saffraan'),
('Salvia'),
('Sint Janskruid'),
('Spirulina'),
('Teunisbloemolie'),
('Valeriaan'),
('Venkel'),
('Vitamine D3 (plantaardig)'),
('Vrouwenmantel'),
('Weegbree'),
('Zaagbladpalm');
"""


sql_script_2 = """
-- Tabel voor klanten
CREATE TABLE IF NOT EXISTS klanten (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naam TEXT NOT NULL,
    emailadres TEXT,
    telefoon TEXT,
    adres TEXT
);

-- Tabel voor notities per klant
CREATE TABLE IF NOT EXISTS notities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER,
    inhoud TEXT,
    datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
);

-- Tabel voor afspraken
CREATE TABLE IF NOT EXISTS afspraken (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER,
    datumtijd TEXT,
    onderwerp TEXT,
    locatie TEXT,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
);
CREATE TABLE IF NOT EXISTS behandelingen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    klant_id INTEGER,
    naam TEXT,
    datum TEXT,
    FOREIGN KEY (klant_id) REFERENCES klanten(id)
);
CREATE TABLE IF NOT EXISTS behandeling_klacht (
    behandeling_id INTEGER,
    klacht_id INTEGER,
    FOREIGN KEY (behandeling_id) REFERENCES behandelingen(id),
    FOREIGN KEY (klacht_id) REFERENCES klachten(id)
);

CREATE TABLE IF NOT EXISTS behandeling_plant (
    behandeling_id INTEGER,
    plant_id INTEGER,
    FOREIGN KEY (behandeling_id) REFERENCES behandelingen(id),
    FOREIGN KEY (plant_id) REFERENCES planten(id)
);

"""
klachten = [
  {
    "naam": "Acne",
    "beschrijving": "Ontstekingen van de huid door verstopte talgklieren, vaak zichtbaar als puistjes of mee-eters."
  },
  {
    "naam": "Aderverkalking",
    "beschrijving": "Ophoping van vetten en kalk in de vaatwanden waardoor bloedvaten vernauwen, verhoogt risico op hart- en vaatziekten."
  },
  {
    "naam": "ADHD",
    "beschrijving": "Aandachtstekortstoornis met hyperactiviteit; gekenmerkt door impulsiviteit, onrust en concentratieproblemen."
  },
  {
    "naam": "Afkicken",
    "beschrijving": "Het proces van het stoppen met verslavende middelen, waarbij ontwenningsverschijnselen optreden."
  },
  {
    "naam": "Afslanken",
    "beschrijving": "Het streven naar gewichtsverlies door voeding, beweging of supplementen, vaak met als doel een betere gezondheid."
  },
  {
    "naam": "Aften",
    "beschrijving": "Kleine, pijnlijke zweertjes in het mondslijmvlies, vaak terugkerend en meestal goedaardig."
  },
  {
    "naam": "Allergie",
    "beschrijving": "Overgevoeligheidsreactie van het immuunsysteem op een onschadelijke stof zoals pollen, voeding of huisstof."
  },
  {
    "naam": "Alcoholmisbruik",
    "beschrijving": "Overmatig alcoholgebruik met negatieve gevolgen voor lichaam, geest en sociale omgeving."
  },
  {
    "naam": "Amandelontsteking",
    "beschrijving": "Ontsteking van de keelamandelen, vaak veroorzaakt door virussen of bacteriën, met keelpijn en slikklachten."
  },
  {
    "naam": "Anti-veroudering",
    "beschrijving": "Behandeling of leefstijl gericht op het vertragen van lichamelijke en mentale verouderingsprocessen."
  },
  {
    "naam": "Anemie",
    "beschrijving": "Verminderde hoeveelheid rode bloedcellen of hemoglobine, wat leidt tot vermoeidheid, duizeligheid en bleke huid."
  },
  {
    "naam": "Angst",
    "beschrijving": "Gevoel van onrust, spanning of paniek zonder directe oorzaak. Kan gepaard gaan met hartkloppingen, zweten en ademhalingsproblemen."
  },
  {
    "naam": "Anorexia",
    "beschrijving": "Een eetstoornis waarbij iemand extreem weinig eet uit angst om aan te komen, met ernstige gevolgen voor gezondheid en psyche."
  },
  {
    "naam": "Artritis",
    "beschrijving": "Ontstekingsziekte van de gewrichten die zwelling, pijn en stijfheid veroorzaakt. Vaak chronisch van aard."
  },
  {
    "naam": "Artrose",
    "beschrijving": "Slijtage van het kraakbeen in gewrichten, waardoor pijn en verminderde beweeglijkheid ontstaan."
  },
  {
    "naam": "Astma",
    "beschrijving": "Chronische ontsteking van de luchtwegen die leidt tot benauwdheid, hoesten en piepende ademhaling."
  },
  {
    "naam": "Baarmoederverzakking",
    "beschrijving": "Aandoening waarbij de baarmoeder naar beneden zakt in de vagina door verzwakte bekkenbodemspieren."
  },
  {
    "naam": "Bedplassen",
    "beschrijving": "Onvrijwillig urineren tijdens de slaap, meestal bij kinderen, maar soms ook bij volwassenen."
  },
  {
    "naam": "Bekkenbodeminstabiliteit",
    "beschrijving": "Verzwakking of disfunctie van de bekkenbodemspieren, wat kan leiden tot urineverlies, rugpijn of verzakkingen."
  },
  {
    "naam": "Bindweefselzwakte",
    "beschrijving": "Erfelijke of verworven verzwakking van het bindweefsel, zichtbaar als bijvoorbeeld spataderen of slappe huid."
  },
  {
    "naam": "Bijholte ontsteking",
    "beschrijving": "Ontsteking van de sinussen, vaak door een verkoudheid, met symptomen als hoofdpijn, druk op het gezicht en verstopte neus."
  },
  {
    "naam": "Blaasontsteking",
    "beschrijving": "Infectie van de blaas, meestal veroorzaakt door bacteriën, met symptomen als branderig gevoel bij het plassen en frequente aandrang."
  }, {
    "naam": "Bloedarmoede",
    "beschrijving": "(Synoniem van anemie) Een tekort aan gezonde rode bloedcellen, waardoor minder zuurstof in het lichaam wordt getransporteerd."
  },
  {
    "naam": "Bloedsuiker (verlaagd)",
    "beschrijving": "Een toestand van hypoglykemie waarbij het bloedsuikerniveau te laag is, wat kan leiden tot duizeligheid, beven en vermoeidheid."
  },
  {
    "naam": "Bloedsuiker (regulerend)",
    "beschrijving": "Verwijst naar ondersteuning van een stabiele bloedsuikerspiegel, met name belangrijk bij diabetespatiënten."
  },
  {
    "naam": "Bloeddruk (regulerend)",
    "beschrijving": "Ondersteunen van een gezonde bloeddruk, zowel bij verhoogde als verlaagde bloeddruk."
  },
  {
    "naam": "Bloeddruk (verhoogd)",
    "beschrijving": "Hypertensie; verhoogde druk in de bloedvaten, wat het risico op hart- en vaatziekten vergroot."
  },
  {
    "naam": "Bloedend tandvlees",
    "beschrijving": "Vaak een symptoom van tandvleesontsteking (gingivitis) of vitaminegebrek, zoals vitamine C."
  },
  {
    "naam": "Bloedzuiverend",
    "beschrijving": "Algemene term voor processen die afvalstoffen uit het bloed helpen verwijderen, vaak gekoppeld aan lever- en nierfunctie."
  },
  {
    "naam": "Bodybuilding",
    "beschrijving": "Spierversterkende activiteit waarbij vaak supplementen of kruiden gebruikt worden ter ondersteuning van spiergroei en herstel."
  },
  {
    "naam": "Borstontsteking (preventief)",
    "beschrijving": "Maatregelen of middelen die helpen ontstekingen in het borstweefsel bij borstvoeding te voorkomen."
  },
  {
    "naam": "Borstvergroting",
    "beschrijving": "Natuurlijke ondersteuning of stimulatie van borstgroei door kruiden of hormonale balans."
  },
  {
    "naam": "Borstvoeding (onvoldoende)",
    "beschrijving": "Probleem waarbij een moeder onvoldoende melk produceert; soms te ondersteunen met galactogogen."
  },
  {
    "naam": "Borstvoeding (afbouwen)",
    "beschrijving": "Het geleidelijk verminderen van borstvoeding, vaak ondersteund met kruiden die de melkproductie remmen."
  },
  {
    "naam": "Borstvoeding (stoppen)",
    "beschrijving": "Het volledig beëindigen van borstvoeding, waarbij bepaalde middelen kunnen helpen de melkproductie sneller te doen stoppen."
  },
  {
    "naam": "Botbreuken",
    "beschrijving": "Ondersteuning van het herstel van gebroken botten, vaak met calciumrijke en weefselherstellende middelen."
  },
  {
    "naam": "Botontkalking",
    "beschrijving": "Ook wel osteoporose; vermindering van de botdichtheid waardoor botten broos worden en sneller breken."
  },
  {
    "naam": "Brandend maagzuur",
    "beschrijving": "Terugvloed van maagzuur naar de slokdarm, wat leidt tot een branderig gevoel in de borststreek."
  },
  {
    "naam": "Branderig gevoel bij het plassen",
    "beschrijving": "Vaak een symptoom van een urineweginfectie of irritatie van de plasbuis."
  },
  {
    "naam": "Bronchitis",
    "beschrijving": "Ontsteking van de luchtpijpvertakkingen (bronchiën), meestal veroorzaakt door virussen of bacteriën, met hoest en slijmvorming."
  },
  {
    "naam": "Buikpijn",
    "beschrijving": "Algemene term voor pijn in de buikstreek, met diverse oorzaken zoals gasvorming, darmproblemen of menstruatie."
  },
  {
    "naam": "Buikvet",
    "beschrijving": "Ophoping van vet rond de buikstreek, vaak gerelateerd aan slechte voeding, stress of hormonale disbalans."
  },
  {
    "naam": "Burn-out",
    "beschrijving": "Een toestand van lichamelijke en geestelijke uitputting, meestal veroorzaakt door langdurige stress of overbelasting."
  },
  {
    "naam": "Candida albicans",
    "beschrijving": "Een schimmelinfectie veroorzaakt door de gist Candida, die overgroeit in de darmen, mond of vagina."
  },
  {
    "naam": "Carpaal Tunnel Syndroom",
    "beschrijving": "Zenuwbeknelling in de pols waardoor pijn, tintelingen of gevoelloosheid in hand en vingers ontstaat."
  },
  {
    "naam": "Cellulitis",
    "beschrijving": "Ophoping van vetcellen en vocht onder de huid, vaak zichtbaar als putjes of bobbeltjes (sinaasappelhuid)."
  },
  {
    "naam": "Cholesterol (te hoog)",
    "beschrijving": "Een verhoogd gehalte aan vetachtige stoffen in het bloed, wat kan leiden tot hart- en vaatziekten."
  },
  {
    "naam": "Colitis ulcerosa",
    "beschrijving": "Chronische ontsteking van de dikke darm die zweren en buikklachten veroorzaakt, soms gepaard met diarree en bloedverlies."
  },
  {
    "naam": "Concentratiezwakte",
    "beschrijving": "Verminderd vermogen om aandacht te houden bij een taak, vaak door stress, vermoeidheid of prikkelgevoeligheid."
  },
  {
    "naam": "Covid-19",
    "beschrijving": "Besmettelijke ziekte veroorzaakt door het coronavirus SARS-CoV-2, met symptomen als koorts, hoest en vermoeidheid."
  },
  {
    "naam": "Crohn (ziekte van)",
    "beschrijving": "Chronische ontstekingsziekte van het maag-darmkanaal die buikpijn, diarree en gewichtsverlies veroorzaakt."
  },
  {
    "naam": "Darmmicrobioom (herstel)",
    "beschrijving": "Het ondersteunen of herstellen van een gezonde balans tussen goede en slechte bacteriën in de darmflora."
  },
  {
    "naam": "Darmkrampen",
    "beschrijving": "Plotselinge samentrekkingen van de darmspieren die pijn en ongemak in de buik veroorzaken."
  },
  {
    "naam": "Darmparasieten",
    "beschrijving": "Ongenode organismen in het spijsverteringskanaal zoals wormen of protozoa, die klachten veroorzaken zoals diarree of buikpijn."
  },
  {
    "naam": "Darmperistaltiek (verminderd)",
    "beschrijving": "Vertraagde beweging van de darmwand die de spijsvertering kan verstoren en constipatie kan veroorzaken."
  },
  {
    "naam": "Dauwworm",
    "beschrijving": "Huiduitslag bij baby’s of jonge kinderen, meestal op het gezicht, vaak veroorzaakt door atopisch eczeem."
  },
  {
    "naam": "Dementie",
    "beschrijving": "Aandoening waarbij cognitieve functies zoals geheugen, taal en oriëntatie achteruitgaan, vaak progressief zoals bij Alzheimer."
  },
  {
    "naam": "Depressiviteit",
    "beschrijving": "Langdurige sombere stemming, verlies van interesse en energie, vaak gepaard met slaapproblemen en negatieve gedachten."
  },
  {
    "naam": "Detox",
    "beschrijving": "Het ondersteunen van de afvoer van afvalstoffen uit het lichaam, vaak via lever, nieren en darmen."
  },
  {
    "naam": "Diabetes",
    "beschrijving": "Chronische stofwisselingsziekte waarbij het lichaam onvoldoende insuline aanmaakt of niet goed reageert op insuline."
  },
  {
    "naam": "Diabetes type 2",
    "beschrijving": "De meest voorkomende vorm van diabetes waarbij de lichaamscellen ongevoelig zijn voor insuline, vaak door leefstijl beïnvloedbaar."
  },
  {
    "naam": "Diarree",
    "beschrijving": "Waterige, frequente ontlasting, vaak veroorzaakt door infecties, voedselintolerantie of darmstoornissen."
  },
  {
    "naam": "Dikke enkels",
    "beschrijving": "Ophoping van vocht of ontsteking rond de enkels, vaak als gevolg van slechte doorbloeding of hartproblemen."
  },
  {
    "naam": "Doorbloedingsstoornissen",
    "beschrijving": "Belemmerde bloedstroom in het lichaam, wat kan leiden tot koude ledematen, krampen of hartproblemen."
  },
  {
    "naam": "Doorslaapproblemen",
    "beschrijving": "Moeite met het in slaap blijven gedurende de nacht, vaak gerelateerd aan stress, angst of hormonale disbalans."
  },
  {
    "naam": "Droge huid",
    "beschrijving": "Een huidconditie waarbij de huid ruw, schilferig of trekkerig aanvoelt, meestal door vochttekort of eczeem."
  },  {
    "naam": "Droogtrainen",
    "beschrijving": "Het verminderen van vetpercentage met behoud van spiermassa, vaak toegepast in bodybuilding."
  },
  {
    "naam": "Duizeligheid",
    "beschrijving": "Gevoel van draaierigheid of instabiliteit, soms gepaard met misselijkheid of flauwvallen."
  },
  {
    "naam": "Dyslexie",
    "beschrijving": "Leerstoornis waarbij het moeilijk is om woorden correct te lezen of te spellen ondanks normale intelligentie."
  },
  {
    "naam": "Dyspraxie",
    "beschrijving": "Motorische ontwikkelingsstoornis waarbij het plannen en uitvoeren van bewegingen moeizaam verloopt."
  },
  {
    "naam": "Eczeem",
    "beschrijving": "Chronische huidontsteking met jeuk, roodheid en schilfers, vaak verergerd door allergie of stress."
  },
  {
    "naam": "Eetlustopwekkend",
    "beschrijving": "Stimuleren van het hongergevoel, vooral bij mensen met verminderde eetlust door ziekte of behandeling."
  },
  {
    "naam": "Emoties",
    "beschrijving": "Innerlijke gemoedstoestanden zoals verdriet, boosheid of blijdschap die invloed hebben op lichamelijk en geestelijk welzijn."
  },
  {
    "naam": "Energietekort",
    "beschrijving": "Een gebrek aan fysieke of mentale energie, vaak door slechte voeding, slaaptekort of onderliggende ziekte."
  },
  {
    "naam": "Epilepsie",
    "beschrijving": "Neurologische aandoening gekenmerkt door aanvallen van tijdelijke stoornissen in de hersenactiviteit (epileptische aanvallen)."
  },
  {
    "naam": "Erectiestoornis",
    "beschrijving": "Het onvermogen om een erectie te krijgen of behouden die voldoende is voor geslachtsgemeenschap."
  },
  {
    "naam": "Examenvrees",
    "beschrijving": "Overmatige angst voor examens of prestatiedruk die leidt tot blokkades of stresssymptomen."
  },
  {
    "naam": "Evenwichtsstoornis",
    "beschrijving": "Moeite met balans en coördinatie, vaak als gevolg van problemen in het binnenoor of zenuwstelsel."
  },
  {
    "naam": "Fibromyalgie",
    "beschrijving": "Chronisch pijnsyndroom met spierpijn, vermoeidheid, slaapstoornissen en concentratieproblemen."
  },
  {
    "naam": "Frigiditeit",
    "beschrijving": "Verminderde zin in seks of het onvermogen om seksuele opwinding of orgasme te ervaren, vaak bij vrouwen."
  },
  {
    "naam": "Futloos",
    "beschrijving": "Een gevoel van energiegebrek, moeheid en gebrek aan motivatie, zonder duidelijke oorzaak."
  },
  {
    "naam": "Galblaasproblemen",
    "beschrijving": "Stoornissen in de werking van de galblaas, zoals ontsteking of galstenen, vaak met pijn in de rechterbovenbuik."
  },
  {
    "naam": "Galstenen",
    "beschrijving": "Verharde afzettingen van galzouten in de galblaas, die pijn en spijsverteringsproblemen kunnen veroorzaken."
  },
  {
    "naam": "Geelzucht",
    "beschrijving": "Geelverkleuring van huid en ogen door een verhoogd bilirubinegehalte, meestal bij lever- of galproblemen."
  },
  {
    "naam": "Geheugenzwakte",
    "beschrijving": "Verminderde mogelijkheid om informatie te onthouden of op te halen, vaak bij stress, ouderdom of neurologische aandoeningen."
  },
  {
    "naam": "Gespannen borsten",
    "beschrijving": "Pijnlijke of gevoelige borsten, meestal door hormonale veranderingen rond menstruatie of zwangerschap."
  },
  {
    "naam": "Gewichtstoename",
    "beschrijving": "Toename van lichaamsgewicht, vaak door ongezonde voeding, hormonale schommelingen of weinig beweging."
  },
  {
    "naam": "Gewrichtsontstekingen",
    "beschrijving": "Ontstekingsreacties in de gewrichten met roodheid, zwelling en pijn, zoals bij artritis."
  },
  {
    "naam": "Gewrichtspijn",
    "beschrijving": "Pijn in een of meerdere gewrichten door slijtage, ontsteking of overbelasting."
  },
  {
    "naam": "Gewrichtsslijtage",
    "beschrijving": "Degeneratie van het kraakbeen in gewrichten (artrose), met stijfheid en bewegingsbeperking."
  },
  {
    "naam": "Gordelroos",
    "beschrijving": "Virale infectie veroorzaakt door het waterpokkenvirus, met pijnlijke blaasjes op de huid in een bandvormig patroon."
  },
  {
    "naam": "Griep",
    "beschrijving": "Virale infectie van de luchtwegen met koorts, spierpijn, vermoeidheid en hoest."
  },
  {
    "naam": "Groei (kinderen)",
    "beschrijving": "Ondersteuning van gezonde groei en ontwikkeling bij kinderen, bijvoorbeeld bij achterblijvende lengte of eetlust."
  },
  {
    "naam": "Haarproblemen (uitval, broos, chemokuur)",
    "beschrijving": "Verzwakking of verlies van haar door stress, voeding, hormonale veranderingen of medische behandeling."
  },
  {
    "naam": "Hart- en vaatziekten (preventie)",
    "beschrijving": "Voorkomen van ziekten zoals hartinfarct of beroerte door gezonde levensstijl en natuurlijke ondersteuning."
  },
  {
    "naam": "Hartkloppingen",
    "beschrijving": "Snelle of onregelmatige hartslag, voelbaar in de borst of keel, soms door stress of hormonale veranderingen."
  },
  {
    "naam": "Hartritmestoornissen",
    "beschrijving": "Afwijkingen in het normale ritme van het hart, wat kan leiden tot duizeligheid, hartkloppingen of flauwvallen."
  },
  {
    "naam": "Herpes simplex",
    "beschrijving": "Virale infectie die blaasjes veroorzaakt op lippen (koortslip) of geslachtsdelen, vaak terugkerend."
  },
  {
    "naam": "Libido (verhoogt)",
    "beschrijving": "Ondersteuning van het seksueel verlangen, bij zowel mannen als vrouwen."
  },
  {
    "naam": "Luchtweginfectie",
    "beschrijving": "Infectie van de luchtwegen, vaak veroorzaakt door virussen of bacteriën, met hoest en benauwdheid."
  },
  {
    "naam": "Luieruitslag",
    "beschrijving": "Irritatie of roodheid van de huid in de luierstreek, vaak veroorzaakt door vocht, wrijving of urine."
  },
  {
    "naam": "Lyme (ziekte van)",
    "beschrijving": "Infectie veroorzaakt door een tekenbeet met de Borrelia-bacterie, met symptomen als huiduitslag, vermoeidheid en gewrichtspijn."
  },
  {
    "naam": "Maagkramp",
    "beschrijving": "Plotselinge pijnlijke samentrekkingen van de maagspieren, vaak door stress, voeding of irritatie van het maagslijmvlies."
  },
  {
    "naam": "Maagpijn",
    "beschrijving": "Pijn of ongemak in de bovenbuik, vaak veroorzaakt door maagzuur, ontsteking of verkeerde voeding."
  },
  {
    "naam": "Maagzuur",
    "beschrijving": "Brandend gevoel in de borst door terugvloei van maagzuur naar de slokdarm (reflux)."
  },
  {
    "naam": "Mee-eters",
    "beschrijving": "Zwarte of witte verstopte poriën op de huid, meestal in het gezicht, veroorzaakt door overmatige talgproductie."
  },
  {
    "naam": "Menopauze",
    "beschrijving": "Overgangsfase waarin de menstruatie stopt, vaak gepaard met opvliegers, stemmingswisselingen en slaapproblemen."
  },
  {
    "naam": "Menstruatieklachten",
    "beschrijving": "Klachten zoals krampen, hoofdpijn en prikkelbaarheid rondom de menstruatiecyclus."
  },
  {
    "naam": "Menstruatiepijn",
    "beschrijving": "Buik- of bekkenpijn tijdens de menstruatie, meestal veroorzaakt door samentrekkingen van de baarmoeder."
  },
  {
    "naam": "Migraine",
    "beschrijving": "Ernstige, vaak eenzijdige hoofdpijn die gepaard kan gaan met misselijkheid, lichtgevoeligheid en visuele verstoringen."
  },
  {
    "naam": "Misselijkheid",
    "beschrijving": "Onprettig gevoel in de maag met de aandrang om te braken, vaak bij infecties of reisziekte."
  },
  {
    "naam": "Misselijkheid (chemokuur)",
    "beschrijving": "Specifieke vorm van misselijkheid veroorzaakt door medicatie tijdens chemotherapie."
  },
  {
    "naam": "Mondflora problemen",
    "beschrijving": "Onevenwicht in de bacteriële balans van de mond, met klachten zoals slechte adem, aften of ontstekingen."
  },
  {
    "naam": "Muisarm (RSI)",
    "beschrijving": "Repetitive Strain Injury door langdurig herhaaldelijk gebruik van arm, pols of hand – vaak bij computerwerk."
  },
  {
    "naam": "Nachtblindheid",
    "beschrijving": "Slecht zien in het donker of bij weinig licht, vaak door tekort aan vitamine A of netvliesproblemen."
  },
  {
    "naam": "Nachtelijk ontwaken",
    "beschrijving": "Het regelmatig wakker worden tijdens de nacht, waardoor de slaapkwaliteit afneemt."
  },
  {
    "naam": "Nachtelijk transpireren",
    "beschrijving": "Overmatig zweten tijdens de slaap, soms gerelateerd aan hormonen of infecties."
  },
  {
    "naam": "Nachtmerries",
    "beschrijving": "Beangstigende of onrustige dromen die leiden tot vroegtijdig ontwaken of angstgevoelens."
  },
  {
    "naam": "Nagels (zwak)",
    "beschrijving": "Breekbare of gespleten nagels, vaak als gevolg van voedingstekorten of externe schade."
  },
  {
    "naam": "Neerslachtigheid",
    "beschrijving": "Langdurig somber of verdrietig gevoel, vaak zonder duidelijke oorzaak."
  },
  {
    "naam": "Nervositeit",
    "beschrijving": "Gevoel van innerlijke onrust, spanning of angst in reactie op stressvolle situaties."
  },
  {
    "naam": "Neusverkoudheid",
    "beschrijving": "Ontsteking van het neusslijmvlies met symptomen als verstopte neus, niezen en loopneus."
  },
  {
    "naam": "Nierstenen",
    "beschrijving": "Vast materiaal gevormd in de nieren dat pijn kan veroorzaken bij het plassen of in de onderrug."
  },
  {
    "naam": "Obesitas",
    "beschrijving": "Ernstig overgewicht met een verhoogd risico op hartziekten, diabetes en gewrichtsklachten."
  },
  {
    "naam": "Obstipatie",
    "beschrijving": "Vertraagde of moeilijke stoelgang, vaak veroorzaakt door voeding, weinig beweging of medicatie."
  },
  {
    "naam": "Oedeem",
    "beschrijving": "Vochtophoping in weefsels, zichtbaar als zwelling, meestal in benen, enkels of handen."
  },
  {
    "naam": "Ogen (droog)",
    "beschrijving": "Verminderde traanproductie of slechte traanfilm, wat leidt tot een branderig of zanderig gevoel in de ogen."
  },
  {
    "naam": "Ontgiften",
    "beschrijving": "Het ondersteunen van de natuurlijke afvoer van toxines uit het lichaam via lever, nieren en huid."
  },
  {
    "naam": "Ontgiften (na antibioticakuur)",
    "beschrijving": "Herstel van darmflora en ondersteuning van leverfunctie na antibioticagebruik."
  },
  {
    "naam": "Ontstekingen",
    "beschrijving": "Reactie van het lichaam op schade of infectie met symptomen als roodheid, zwelling en pijn."
  },
  {
    "naam": "Oogklachten",
    "beschrijving": "Algemene klachten zoals branderige, vermoeide of tranende ogen door allergie, droogte of infecties."
  },
  {
    "naam": "Oorsuizen",
    "beschrijving": "Perceptie van geluid (zoals suizen of piepen) zonder externe bron, ook wel tinnitus genoemd."
  },
  {
    "naam": "Opgeblazen gevoel",
    "beschrijving": "Gevoel van druk of volheid in de buik, vaak veroorzaakt door gasvorming of langzame spijsvertering."
  },
  {
    "naam": "Opgroeiende kinderen",
    "beschrijving": "Fase van fysieke en mentale ontwikkeling waarbij goede voeding en ondersteuning cruciaal zijn."
  },
  {
    "naam": "Opspringen",
    "beschrijving": "Plotselinge spiercontracties of ongecontroleerde bewegingen, soms gerelateerd aan stress of reflexen."
  },
  {
    "naam": "Opvliegers",
    "beschrijving": "Plotselinge warmteaanvallen met roodheid en zweten, vaak tijdens de menopauze."
  },
  {
    "naam": "Osteoporose",
    "beschrijving": "Afname van botdichtheid, waardoor botten broos worden en makkelijker breken."
  },
  {
    "naam": "Overactiviteit (bij kinderen)",
    "beschrijving": "Moeite met stilzitten of concentreren, vaak gezien bij ADHD of prikkelgevoeligheid."
  },
  {
    "naam": "Overgangsklachten",
    "beschrijving": "Fysieke en mentale symptomen die optreden tijdens de menopauze, zoals stemmingswisselingen en slapeloosheid."
  },
  {
    "naam": "Overgeven",
    "beschrijving": "Het krachtig legen van de maag via de mond, vaak als reactie op misselijkheid, infectie of vergiftiging."
  },
  {
    "naam": "Overgewicht",
    "beschrijving": "Hoger lichaamsgewicht dan gezond is voor lengte en leeftijd, met risico op metabole aandoeningen."
  },
  {
    "naam": "Parodontitis",
    "beschrijving": "Ontsteking van het tandvlees en kaakbot, vaak leidend tot terugtrekkend tandvlees en tandverlies."
  },
  {
    "naam": "Peesontsteking",
    "beschrijving": "Ontsteking van een pees, meestal veroorzaakt door overbelasting of herhaalde bewegingen."
  },
  {
    "naam": "Pfeiffer (ziekte van)",
    "beschrijving": "Virale infectie (Epstein-Barr-virus) met symptomen zoals vermoeidheid, koorts en opgezette klieren."
  },
  {
    "naam": "Plankenkoorts",
    "beschrijving": "Angst of spanning om voor een publiek te spreken of op te treden, ook bekend als podiumvrees."
  },
  {
    "naam": "Plasproblemen",
    "beschrijving": "Moeite met plassen, vaak in de vorm van pijn, aandrang of een zwakke straal."
  },
  {
    "naam": "Premenstrueel syndroom (PMS)",
    "beschrijving": "Klachten zoals prikkelbaarheid, buikpijn en vermoeidheid voorafgaand aan de menstruatie."
  },
  {
    "naam": "Prestatieverbetering (lichamelijk en geestelijk)",
    "beschrijving": "Verbeteren van fysieke of mentale prestaties, bijvoorbeeld bij sporters of studenten."
  },
  {
    "naam": "Prestatievermindering",
    "beschrijving": "Afname van energie, concentratie of fysieke kracht, vaak bij stress, burn-out of ziekte."
  },
  {
    "naam": "Prikkelbaar Darm Syndroom",
    "beschrijving": "Chronische darmstoornis met symptomen als buikpijn, krampen, winderigheid en wisselende stoelgang."
  },
  {
    "naam": "Prikkelbaarheid",
    "beschrijving": "Gemakkelijk geïrriteerd of gespannen reageren op situaties, vaak door vermoeidheid of hormonale schommelingen."
  },
  {
    "naam": "Prostaatvergroting",
    "beschrijving": "Vergroting van de prostaatklier bij mannen, wat kan leiden tot plasproblemen."
  },
  {
    "naam": "Psoriasis",
    "beschrijving": "Chronische huidziekte met rode, schilferige plekken, vaak op ellebogen, knieën en hoofdhuid."
  },
  {
    "naam": "Reiniging",
    "beschrijving": "Ondersteunen van de interne reiniging van organen zoals lever, darmen en huid."
  },
  {
    "naam": "Reiziekte",
    "beschrijving": "Misselijkheid, duizeligheid en zweten veroorzaakt door beweging tijdens reizen met auto, boot of vliegtuig."
  },
  {
    "naam": "Reuma",
    "beschrijving": "Verzamelnaam voor ontstekingsziekten van gewrichten, vaak met pijn, zwelling en stijfheid."
  },
  {
    "naam": "Rimpels",
    "beschrijving": "Lijntjes of plooien in de huid door veroudering, zonneschade of verminderde collageenproductie."
  },
  {
    "naam": "Rugpijn",
    "beschrijving": "Pijn in de onder-, midden- of bovenrug, veroorzaakt door overbelasting, stress of slechte houding."
  },
  {
    "naam": "Schimmelinfecties (Candida albicans)",
    "beschrijving": "Infecties veroorzaakt door gistachtige schimmel, vaak in huidplooien, mond of intieme zone."
  },
  {
    "naam": "Seksueel onvermogen",
    "beschrijving": "Moeite met seksueel functioneren, zoals erectiestoornis of gebrek aan libido."
  },
  {
    "naam": "Sinaasappelhuid",
    "beschrijving": "Populaire benaming voor cellulitis: bobbelige huidstructuur door vet- en vochtophoping."
  },
  {
    "naam": "Sinusitis",
    "beschrijving": "Ontsteking van de bijholtes, vaak gepaard met hoofdpijn, druk in het gezicht en verstopte neus."
  },
  {
    "naam": "Slaapproblemen",
    "beschrijving": "Moeite met in slaap vallen of doorslapen, wat leidt tot vermoeidheid overdag."
  },
  {
    "naam": "Slapeloosheid",
    "beschrijving": "Langdurige moeite met slapen, vaak veroorzaakt door stress, piekeren of hormonale veranderingen."
  },
  {
    "naam": "Slechte adem",
    "beschrijving": "Onaangename geur uit de mond, meestal veroorzaakt door bacteriën op de tong of in het tandvlees."
  },
  {
    "naam": "Slijmbeursontsteking",
    "beschrijving": "Ontsteking van een slijmbeurs (bursa), vaak in schouder, elleboog of heup, met zwelling en pijn."
  },
  {
    "naam": "Snoepzucht",
    "beschrijving": "Sterke behoefte aan zoetigheid, vaak als gevolg van bloedsuikerschommelingen of emotioneel eten."
  },

  {
    "naam": "Sombere stemmingen",
    "beschrijving": "Tijdelijke of aanhoudende gevoelens van verdriet of negativiteit, zonder duidelijke oorzaak."
  },
  {
    "naam": "Spanningshoofdpijn",
    "beschrijving": "Hoofdpijn door spierspanning of stress, meestal voelbaar als een drukkende band om het hoofd."
  },
  {
    "naam": "Spermavorming (gering)",
    "beschrijving": "Verminderde productie of kwaliteit van zaadcellen, met mogelijke invloed op vruchtbaarheid."
  },
  {
    "naam": "Spierpijn",
    "beschrijving": "Pijnlijke spieren na inspanning, overbelasting of ontsteking."
  },
  {
    "naam": "Spiermassa (vergroten)",
    "beschrijving": "Het doelgericht vergroten van spieromvang, meestal door training en voeding."
  },
  {
    "naam": "Spit",
    "beschrijving": "Acute lage rugpijn als gevolg van een spierverrekking of irritatie van de tussenwervelschijven."
  },
  {
    "naam": "Sportinspanning",
    "beschrijving": "Lichamelijke activiteit waarbij het lichaam extra ondersteuning of herstel kan gebruiken."
  },
  {
    "naam": "Spijsverteringsstoornissen",
    "beschrijving": "Verstoorde werking van het spijsverteringskanaal, met klachten als opgeblazen gevoel, misselijkheid of diarree."
  },
  {
    "naam": "Steenpuisten",
    "beschrijving": "Diepe ontstekingen van haarzakjes, meestal veroorzaakt door bacteriën, met pijnlijke rode bulten."
  },
  {
    "naam": "Stemmingswisselingen",
    "beschrijving": "Plotselinge veranderingen in stemming, vaak veroorzaakt door hormonen, stress of psychische klachten."
  },
  {
    "naam": "Stress",
    "beschrijving": "Langdurige spanning of overbelasting, zowel mentaal als fysiek, vaak met uitputtingsklachten."
  },
  {
    "naam": "Stress (kortstondig)",
    "beschrijving": "Tijdelijke vorm van spanning of druk, bijvoorbeeld bij deadlines of onverwachte gebeurtenissen."
  },
  {
    "naam": "Stress (oxidatief)",
    "beschrijving": "Celbeschadiging door vrije radicalen, vaak in verband met veroudering en chronische ziekten."
  },
  {
    "naam": "Stoelgangproblemen",
    "beschrijving": "Veranderingen in frequentie, structuur of moeite met de ontlasting."
  },
  {
    "naam": "Suikerziekte (ouderdoms)",
    "beschrijving": "Type 2 diabetes, waarbij het lichaam minder gevoelig is voor insuline, vaak op latere leeftijd."
  },
  {
    "naam": "Tabaksverslaving (ondersteunend)",
    "beschrijving": "Ondersteuning bij het stoppen met roken, gericht op ontwenningsverschijnselen en motivatie."
  },
  {
    "naam": "Tendinitis",
    "beschrijving": "Ontsteking van een pees, vaak in schouder, elleboog of knie, veroorzaakt door overbelasting."
  },
  {
    "naam": "Tennisarm",
    "beschrijving": "Pijnlijke aandoening aan de buitenkant van de elleboog door overbelasting van de onderarmspieren."
  },
  {
    "naam": "Tinnitus",
    "beschrijving": "Aanhoudend oorsuizen of piepen zonder externe geluidsbron, vaak als gevolg van gehoorbeschadiging."
  },
  {
    "naam": "Tintelingen in handen en voeten",
    "beschrijving": "Prikkelend of doof gevoel, vaak door beknelde zenuwen of slechte doorbloeding."
  },
  {
    "naam": "Traumaverwerking",
    "beschrijving": "Het verwerken van ingrijpende gebeurtenissen, zowel lichamelijk als emotioneel."
  },
  {
    "naam": "Triglyceridengehalte (te hoog)",
    "beschrijving": "Verhoogde vetwaarden in het bloed, wat het risico op hart- en vaatziekten verhoogt."
  },
  {
    "naam": "Uithoudingsvermogen (verminderd)",
    "beschrijving": "Verminderde fysieke energie of conditie bij inspanning, vaak bij ziekte of uitputting."
  },
  {
    "naam": "Uitputting",
    "beschrijving": "Gevoel van totale vermoeidheid, zowel mentaal als fysiek, vaak door langdurige stress of ziekte."
  },
  {
    "naam": "Urine (sterk geurend)",
    "beschrijving": "Afwijkende geur van urine, mogelijk door infectie, uitdroging of voeding."
  },
  {
    "naam": "Urineproductie (gering)",
    "beschrijving": "Verminderde hoeveelheid urine, mogelijk door vochttekort of nierproblemen."
  },
  {
    "naam": "Urineweginfecties",
    "beschrijving": "Ontstekingen van de urinewegen, vaak met pijn bij het plassen en frequente aandrang."
  },
  {
    "naam": "Urineverlies (vrouwen)",
    "beschrijving": "Ongewild verlies van urine, vaak door verzwakte bekkenbodemspieren of hormonale veranderingen."
  },
  {
    "naam": "Vaginitis",
    "beschrijving": "Ontsteking van de vagina, met klachten als jeuk, afscheiding en roodheid, vaak door infecties of irritatie."
  },
  {
    "naam": "Vergeetachtigheid",
    "beschrijving": "Moeite om informatie te onthouden of herinneren, soms door stress, vermoeidheid of ouderdom."
  },
  {
    "naam": "Verkoudheid",
    "beschrijving": "Virusinfectie van de bovenste luchtwegen, met symptomen als niezen, loopneus en keelpijn."
  },
  {
    "naam": "Vermagering",
    "beschrijving": "Onbedoeld gewichtsverlies door ziekte, stress of spijsverteringsproblemen."
  },
  {
    "naam": "Vermoeidheid",
    "beschrijving": "Algemeen gevoel van moeheid of gebrek aan energie, zonder directe oorzaak."
  },
  {
    "naam": "Vermoeidheid (chronisch)",
    "beschrijving": "Langdurige en aanhoudende moeheid die dagelijkse activiteiten belemmert, vaak zonder duidelijke oorzaak."
  },
  {
    "naam": "Veroudering",
    "beschrijving": "Natuurlijke achteruitgang van lichaam en geestelijke functies naarmate men ouder wordt."
  },
  {
    "naam": "Verstoorde darmflora",
    "beschrijving": "Onevenwicht in de darmbacteriën, vaak door antibiotica of slechte voeding."
  },
  {
    "naam": "Verstopping",
    "beschrijving": "Moeizame stoelgang met harde ontlasting, vaak veroorzaakt door vezelarme voeding of te weinig vocht."
  },
  {
    "naam": "Vetophoping (plaatselijk)",
    "beschrijving": "Plaatselijke vetophoping op buik, dijen of billen, vaak hormonaal of genetisch bepaald."
  },
  {
    "naam": "Vetverbranding",
    "beschrijving": "Proces waarbij opgeslagen vet als energiebron wordt gebruikt, vaak gestimuleerd door beweging of dieet."
  },
  {
    "naam": "Vitaliteit (verminderd)",
    "beschrijving": "Afname van levenslust en energie, vaak bij stress, ziekte of hormonale schommelingen."
  },
  {
    "naam": "Vochtafdrijving",
    "beschrijving": "Stimulatie van de afvoer van overtollig vocht via urine, bij oedeem of hoge bloeddruk."
  },
  {
    "naam": "Voedselvergiftiging",
    "beschrijving": "Plotselinge klachten zoals diarree, misselijkheid en braken door besmet voedsel."
  },
  {
    "naam": "Voetschimmel",
    "beschrijving": "Schimmelinfectie tussen de tenen of op de voetzool, vaak met jeuk, schilfering en geur."
  },
  {
    "naam": "Voorhoofdsholteontsteking",
    "beschrijving": "Ontsteking van de sinussen in het voorhoofd, vaak na een verkoudheid, met drukpijn en verstopte neus."
  },
  {
    "naam": "Vruchtbaarheid (verhoogend)",
    "beschrijving": "Ondersteuning van het voortplantingssysteem om de kans op zwangerschap te vergroten."
  },
  {
    "naam": "Weerstand (winter)",
    "beschrijving": "Verminderde afweer tijdens de koude maanden, met verhoogde vatbaarheid voor verkoudheden en griep."
  },
  {
    "naam": "Windigheid",
    "beschrijving": "Overmatige gasvorming in de darmen met winderigheid en een opgeblazen gevoel."
  },
  {
    "naam": "Witte vloed",
    "beschrijving": "Normale of abnormale vaginale afscheiding, afhankelijk van hoeveelheid, kleur en geur."
  },
  {
    "naam": "Zonlicht (gebrek aan)",
    "beschrijving": "Tekort aan zonlicht, vaak leidend tot vitamine D-tekort of seizoensgebonden depressie."
  },
  {
    "naam": "Zuur-base evenwicht",
    "beschrijving": "Balans tussen zuren en basen in het lichaam, essentieel voor een goede stofwisseling."
  },
  {
    "naam": "Zwaarlijvigheid",
    "beschrijving": "Ernstige vorm van overgewicht, met verhoogd risico op hart- en vaatziekten, diabetes en gewrichtsklachten."
  },
  {
    "naam": "Zwangerschapsbraken",
    "beschrijving": "Misselijkheid en braken in de eerste maanden van de zwangerschap, ook bekend als ochtendmisselijkheid."
  },
  {
    "naam": "Zwangerschapsstriemen",
    "beschrijving": "Huidstriemen door snelle uitrekking tijdens de zwangerschap, vaak op buik, heupen of borsten."
  },
  {
    "naam": "Zweetvoeten",
    "beschrijving": "Overmatige transpiratie aan de voeten, vaak met geur en schimmelvorming."
  }
]

with open('klachten.json', 'w', encoding='utf-8') as f:
    json.dump(klachten, f, ensure_ascii=False, indent=2)

print("JSON-bestand is opgeslagen als 'klachten.json'")

# ✅ Alles in één nette transactie
with sqlite3.connect("fytotherapie.db") as conn:
    cursor = conn.cursor()

    # Voer SQL-scripts uit
    cursor.executescript(sql_script_1)
    cursor.executescript(sql_script_2)

    print("Database en tabellen aangemaakt ✅")

    # Klachten uit CSV importeren
    df = pd.read_csv("Klachten_met_Beschrijving_OPGESCHOOND.csv")


    print("✅ Klachten succesvol geïmporteerd in de database.")

conn = sqlite3.connect('fytotherapie.db')  # <-- Pas dit aan naar jouw bestandsnaam
cursor = conn.cursor()


# Stap 3: Lees de JSON-file in
with open('klachten.json', 'r', encoding='utf-8') as f:
    klachten_lijst = json.load(f)

# Stap 4: Voeg elk item toe aan de database
# Voeg elk item toe aan de database
for klacht in klachten_lijst:
    cursor.execute(
        "INSERT INTO klachten (naam, beschrijving) VALUES (?, ?)",
        (klacht["naam"], klacht["beschrijving"])
    )

# ✅ Eerst committen
conn.commit()

# ✅ Dan pas sluiten
conn.close()


print("✅ JSON succesvol toegevoegd aan de database.")
