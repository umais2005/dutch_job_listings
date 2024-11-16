job_listing_json_prompt = """
Analyseer de volgende vacaturetekst en geef de informatie terug in JSON-indeling met de volgende sleutels en waarden in het Nederlands:

- **Job title:** De functietitel, waarbij alleen de kern wordt weergegeven door beschrijvende woorden of extra details te verwijderen (bijvoorbeeld 'Ervaren tandartsassistent algemene praktijk' wordt 'tandartsassistent').
- **Job description:** De volledige functiebeschrijving inclusief alle belangrijke details over verantwoordelijkheden, kwalificaties, vereisten en voordelen, exact zoals gegeven in de vacaturetekst, zonder wijzigingen.
- **Location:** De locatie die in de vacaturetekst wordt vermeld, in het formaat 'stad, staat, land.' Als de functie op afstand is of geen locatie heeft, gebruik dan 'Nederland'.
- **Contract Details:** Altijd 'Deeltijd'.
- **Job Industry:** Altijd 'Medisch / Farmaceutisch'.
- **Client:** Altijd 'Fleming'.

Gebruik het volgende JSON-formaat en zorg dat alle waarden in het Nederlands zijn:

```
<curly brackets open>
    "Job title": "Titel",
    "Job description": "De volledige functiebeschrijving inclusief alle belangrijke details over verantwoordelijkheden, kwalificaties, vereisten en voordelen, exact zoals gegeven in de vacaturetekst, zonder wijzigingen.",
    "Location": "stad, staat, land",
    "Contract Details": "Deeltijd",
    "Job Industry": "Medisch / Farmaceutisch",
    "Client": "Fleming"
<curly brackets close>
```

Geef alleen de JSON-output.

Hier is de vacaturetekst: 

{job_listing}
"""


rewrite_prompt = """
Herschrijf alleen de functiebeschrijving van de volgende vacaturetekst om unieke inhoud te creëren. Behoud alle essentiële details, verantwoordelijkheden en kwalificaties, maar gebruik andere zinsconstructies, synoniemen en een frisse structuur waar mogelijk. Zorg ervoor dat de herschreven functiebeschrijving dezelfde toon en intentie behoudt als het origineel.

Belangrijk:

Verwijder strikt alle specifieke namen, telefoonnummers, e-mailadressen, website links, of andere herkenbare details van klinieken, bedrijven, merken, of contactpersonen. Geen enkele vorm van contactinformatie mag aanwezig zijn in de herschreven tekst.
Gebruik de volgende afsluitende zin zonder extra contactinformatie:
'Enthousiast? Solliciteer dan direct via de onderstaande button.'
Indien er geen specifieke locatie is vermeld in de functieomschrijving, voeg dan 'Nederland' toe als locatie.

Het output moet volledig anoniem zijn en in het Nederlands.

Hier is de functiebeschrijving: {job_listing}
    """

to_html ="""
You are a html generator which outputs only html text, without any descriptions, explanations, or code block indicators. The output should be plain HTML only—no extra formatting or introductory text should appear in the response.
Convert the following markdown text into HTML format, organizing the content with appropriate tags and removing any markdown formatting. Use `<h1>`, `<h2>`, or `<h3>` tags for main and subheadings, `<p>` tags for paragraphs, and `<li>` tags within `<ul>` lists for any list items you detect. Ensure the structure is clear and logical
The response should contain:
  2. Heading tags that should reflect the hierarchy of the content, with the main topic as `<h1>`, subtopics as `<h2>`, and any further details as `<h3>`.
  3. Use `<p>` tags for regular paragraphs.
  4. If there is a list, use `<ul>` to wrap the list and `<li>` tags for each item.
  5. Check if there is a line similar to '<p><strong>Enthousiast?</strong><br> Solliciteer dan direct via de onderstaande button.</p>' at the end of the text. If a similar line is not present, add this line at the end. If it is, leave the text as it is.
Example:
Input text: '**Introduction to HTML**. HTML stands for HyperText Markup Language. Common elements include headings, paragraphs, and lists such as ordered and unordered.'

Output (HTML):

<h1>Introduction to HTML</h1>
<p>HTML stands for HyperText Markup Language.</p>
<p>Common elements include:</p>
<ul>
  <li>Headings</li>
  <li>Paragraphs</li>
  <li>Lists such as ordered and unordered</li>
</ul>


Text to convert:
{text}"

"""