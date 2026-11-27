# Presidents Work — website (Realistic House, v14)

A static site: open `index.html` and everything runs. No build step.

## What's here

    index.html        the whole site: the 3D house walk, every page, all scripts and styles
    img/              page photography, paintings, program icons, client logos, founder portrait
    work/<project>/   case-study media, one folder per project (card.jpg, hero.jpg, 01.jpg …, .mp4)
    fonts/            Instrument Serif, Freigeist, Neue Haas Grotesk Display, Palmer Lake
    js/               the Lottie player for the Method page's brand wheel
    favicon.png, apple-touch-icon.png, og-image.jpg

## Pages (hash routes)

    #top          the house walk (home)
    #index        selected work, references, clients
    #programs     all programs (linked from the footer)
    #launch #boardroom #formation #elevation #enterprise #direction
    #method       the Presidential Run through the Rose Garden (3D)
    #about  #yankyperl  #contact
    #specialtyrx #pyle #hireends #spritzonme #pedal #moonwalk-orthotics   case studies

## Before going live

- Point `og:image` and `twitter:image` in `index.html` at the full URL, e.g.
  `https://presidentswork.com/og-image.jpg`, so link previews show the image.
- The contact form has no backend yet; it opens an email draft to hello@presidentswork.com.
- The work data mirrors `site.js` in presidentswork/presidents-work (the WORK array and work/ folders).
