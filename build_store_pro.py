from pathlib import Path
from html import escape
import json
import re

CATALOG=json.loads(Path("store-products.json").read_text(encoding="utf-8"))
WORDS={
"fr":{
  "eyebrow":"BOUTIQUE LOCALE · IMSFRANE CATHÉDRALE",
  "heroTitle":"Les trésors de l’Atlas, <em>tout simplement.</em>",
  "heroText":"Une boutique inspirée du plein air, avec des produits du terroir sélectionnés dans les montagnes de notre région.",
  "browse":"Explorer les produits","contact":"Une question ?","small":"Sélection locale","noFake":"Produits de l’Atlas","orderDirect":"Commande directe","check":"Disponibilité confirmée avant commande",
  "step1":"Choisissez vos produits","step2":"Préparez votre panier","step3":"Confirmez sur WhatsApp",
  "sidebar":"Explorer la boutique","catalog":"Notre sélection","all":"Tous les produits",
  "honey":"Miels de montagne","oil":"Huiles locales","herbs":"Plantes & aromates",
  "count":"produits","single":"produit","search":"Rechercher un produit…","searchLabel":"Rechercher dans la boutique",
  "sort":"Trier","featured":"Notre sélection","cheap":"Prix croissant","expensive":"Prix décroissant",
  "cardKicker":"PRODUIT LOCAL","buy":"Ajouter au panier","unit":"MAD","details":"Voir le produit","inquire":"Infos & disponibilité",
  "empty":"Aucun produit ne correspond à votre recherche.","reset":"Effacer les filtres",
  "trustHeadline":"Une boutique à taille humaine","trustTitle":"Des produits qui racontent notre région",
  "trustText":"Découvrez une sélection simple de saveurs des montagnes de l’Atlas. Pas de paiement en ligne : chaque demande est confirmée directement avec notre équipe.",
  "trustItems":["Produits de notre région","Échange direct avec une équipe locale","Quantités et livraison à confirmer"],
  "cart":"Mon panier","cartEmpty":"Votre panier attend ses premières découvertes.","cartSub":"Choisissez un ou plusieurs produits pour préparer votre demande.",
  "subtotal":"Total indicatif","qty":"Quantité","remove":"Retirer","close":"Fermer le panier",
  "checkout":"Commander via WhatsApp","cartHint":"Demande sans paiement. Quantités, conditionnement, prix final, livraison et disponibilité à confirmer.",
  "cartAdded":"Produit ajouté au panier","cartRemoved":"Produit retiré du panier",
  "messageTitle":"DEMANDE DE COMMANDE — BOUTIQUE IMSFRANE","messageAvailability":"Merci de confirmer la disponibilité, les quantités, le conditionnement, le prix final et la livraison.",
  "filterLabel":"Filtrer les produits","currency":"MAD","viewCart":"Voir mon panier",
  "banner":"À découvrir · Saveurs des montagnes marocaines","three":"3 références actuelles · d’autres à venir",
  "breadcrumb":"Accueil","shop":"Boutique"
},
"en":{
  "eyebrow":"LOCAL SHOP · IMSFRANE CATHÉDRALE",
  "heroTitle":"The best of the Atlas, <em>naturally.</em>",
  "heroText":"An outdoor-inspired boutique offering a carefully selected range of natural products from our mountain region.",
  "browse":"Explore products","contact":"Any questions?","small":"Local selection","noFake":"Atlas products","orderDirect":"Direct ordering","check":"Availability confirmed before ordering",
  "step1":"Choose your products","step2":"Build your basket","step3":"Confirm on WhatsApp",
  "sidebar":"Shop by category","catalog":"Our collection","all":"All products",
  "honey":"Mountain honey","oil":"Local olive oils","herbs":"Wild herbs",
  "count":"products","single":"product","search":"Search for a product…","searchLabel":"Search the shop",
  "sort":"Sort by","featured":"Featured","cheap":"Price: low to high","expensive":"Price: high to low",
  "cardKicker":"LOCAL PRODUCT","buy":"Add to basket","unit":"MAD","details":"View product","inquire":"Info & availability",
  "empty":"No products match your search.","reset":"Clear filters",
  "trustHeadline":"A shop with a personal touch","trustTitle":"Products with roots in the Atlas",
  "trustText":"Discover a curated selection of local mountain flavours. No online payment: our team personally confirms every order request.",
  "trustItems":["Products from our region","Direct contact with a local team","Availability and delivery to be confirmed"],
  "cart":"Your basket","cartEmpty":"Your basket is waiting for its first discoveries.","cartSub":"Choose one or more products to prepare your request.",
  "subtotal":"Indicative total","qty":"Quantity","remove":"Remove","close":"Close basket",
  "checkout":"Order via WhatsApp","cartHint":"No online payment. Packaging, quantities, final prices, delivery and availability are subject to confirmation.",
  "cartAdded":"Added to basket","cartRemoved":"Removed from basket",
  "messageTitle":"ORDER REQUEST — IMSFRANE SHOP","messageAvailability":"Please confirm availability, quantity, packaging, final price and delivery options.",
  "filterLabel":"Filter products","currency":"MAD","viewCart":"View basket",
  "banner":"Discover · Flavours of Morocco’s mountains","three":"3 products available to enquire about · more coming",
  "breadcrumb":"Home","shop":"Shop"
}
}
CATEGORY_KEYS=("all","honey","oil","herbs")

def e(s):
    return escape(str(s),quote=True)

def render(lang):
    t=WORDS[lang]
    nav="".join('<button class="sp-cat" type="button" data-category="'+key+'" aria-pressed="'+str(key=="all").lower()+'"><span>'+e(t[key])+'</span><b>'+str(len(CATALOG["products"]) if key=="all" else sum(p["category"]==key for p in CATALOG["products"]))+'</b></button>' for key in CATEGORY_KEYS)
    chips="".join('<button class="sp-chip" data-category="'+key+'" type="button" aria-pressed="'+str(key=="all").lower()+'">'+e(t[key])+'</button>' for key in CATEGORY_KEYS)
    items=[]
    for p in CATALOG["products"]:
        name=e(p["nameFr" if lang=="fr" else "nameEn"])
        desc=e(p["shortFr" if lang=="fr" else "shortEn"])
        unit=e(p["unitFr" if lang=="fr" else "unitEn"])
        img="../images/"+e(p["image"])
        items.append(
          '<article class="sp-card" data-product="'+e(p["id"])+'" data-category="'+e(p["category"])+'" data-price="'+str(p["price"])+'" data-search="'+e((p["nameFr"]+" "+p["nameEn"]+" "+p["shortFr"]+" "+p["shortEn"]).lower())+'">'
          '<div class="sp-photo"><img loading="lazy" decoding="async" alt="'+e(p["imageAltFr" if lang=="fr" else "imageAltEn"])+'" src="'+img+'">'
          '<span class="sp-photo-label">'+e(t["cardKicker"])+'</span></div>'
          '<div class="sp-card-body"><span class="sp-card-category">'+e(t[p["category"]])+'</span><h3>'+name+'</h3>'
          '<p class="sp-card-description">'+desc+'</p><div class="sp-card-bottom">'
          '<div class="sp-price">'+str(p["price"])+' <small>MAD</small><span>'+unit+'</span></div>'
          '<button class="sp-add" type="button" data-add="'+e(p["id"])+'" aria-label="'+e(t["buy"]+" : "+name)+'">'
          '<i class="fa-solid fa-plus" aria-hidden="true"></i><span>'+e(t["buy"])+'</span></button>'
          '</div></div></article>'
        )
    benefits="".join('<li><i class="fa-solid fa-check" aria-hidden="true"></i>'+e(x)+'</li>' for x in t["trustItems"])
    return f'''<main id="imsfrane-shop" class="sp-main">
    <section class="sp-hero" aria-labelledby="sp-title">
      <div class="sp-hero-inner">
        <div class="sp-hero-left">
          <div class="sp-breadcrumb"><a href="index.html">{e(t["breadcrumb"])}</a><span>/</span><span>{e(t["shop"])}</span></div>
          <span class="sp-eyebrow"><i class="fa-solid fa-mountain-sun" aria-hidden="true"></i> {e(t["eyebrow"])}</span>
          <h1 id="sp-title">{t["heroTitle"]}</h1><p>{e(t["heroText"])}</p>
          <div class="sp-hero-actions"><a class="sp-hero-button" href="#sp-products">{e(t["browse"])} <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a>
          <a class="sp-hero-link" href="https://wa.me/{CATALOG["whatsapp"]}" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-whatsapp" aria-hidden="true"></i> {e(t["contact"])}</a></div>
        </div>
        <div class="sp-hero-feature" aria-label="{e(t["banner"])}">
          <div class="sp-hero-feature-art" aria-hidden="true"><i class="fa-solid fa-mountain-sun"></i></div>
          <span class="sp-hero-feature-tag">{e(t["small"])}</span>
          <strong>{e(t["noFake"])}</strong><p>{e(t["three"])}</p>
          <div class="sp-hero-feature-footer">{e(t["banner"])}</div>
        </div>
      </div>
    </section>
    <div class="sp-benefits"><div class="sp-benefits-inner">
      <div><i class="fa-solid fa-seedling" aria-hidden="true"></i><span>{e(t["noFake"])}</span></div>
      <div><i class="fa-brands fa-whatsapp" aria-hidden="true"></i><span>{e(t["orderDirect"])}</span></div>
      <div><i class="fa-solid fa-shield-heart" aria-hidden="true"></i><span>{e(t["check"])}</span></div>
    </div></div>
    <div class="sp-shell" id="sp-products">
      <aside class="sp-sidebar" aria-label="{e(t["sidebar"])}"><div class="sp-side-inner">
        <div class="sp-sidebar-head"><i class="fa-solid fa-list" aria-hidden="true"></i><h2>{e(t["sidebar"])}</h2></div>
        <nav class="sp-category-nav" aria-label="{e(t["filterLabel"])}">{nav}</nav>
        <div class="sp-side-note"><i class="fa-solid fa-circle-info" aria-hidden="true"></i><p>{e(t["cartHint"])}</p></div>
      </div></aside>
      <section class="sp-catalog" aria-labelledby="sp-catalog-title">
        <div class="sp-catalog-heading"><div><span class="sp-section-eyebrow">IMSFRANE CATHÉDRALE / SHOP</span><h2 id="sp-catalog-title">{e(t["catalog"])}</h2></div>
          <button class="sp-cart-open" id="sp-cart-open" type="button" aria-haspopup="dialog" aria-controls="sp-cart">
            <i class="fa-solid fa-basket-shopping" aria-hidden="true"></i><span>{e(t["cart"])}</span><b id="sp-cart-count">0</b>
          </button></div>
        <div class="sp-tools">
          <label class="sp-search"><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i><span class="sp-visually-hidden">{e(t["searchLabel"])}</span><input id="sp-search" type="search" placeholder="{e(t["search"])}" autocomplete="off"></label>
          <label class="sp-sort"><span>{e(t["sort"])}</span><select id="sp-sort"><option value="featured">{e(t["featured"])}</option><option value="asc">{e(t["cheap"])}</option><option value="desc">{e(t["expensive"])}</option></select></label>
        </div>
        <div class="sp-chips" id="sp-chips" role="group" aria-label="{e(t["filterLabel"])}">{chips}</div>
        <p id="sp-results" class="sp-results" role="status" aria-live="polite">3 {e(t["count"])}</p>
        <div class="sp-grid" id="sp-grid">{"".join(items)}</div>
        <div id="sp-no-results" class="sp-no-results" hidden><i class="fa-solid fa-magnifying-glass" aria-hidden="true"></i><p>{e(t["empty"])}</p><button type="button" id="sp-clear">{e(t["reset"])}</button></div>
      </section>
    </div>
    <section class="sp-story" aria-labelledby="sp-story-title"><div class="sp-story-inner">
      <div><span class="sp-section-eyebrow">{e(t["trustHeadline"])}</span><h2 id="sp-story-title">{e(t["trustTitle"])}</h2><p>{e(t["trustText"])}</p></div>
      <ul>{benefits}</ul>
    </div></section>
    <div class="sp-modal-backdrop" id="sp-backdrop" hidden></div>
    <aside class="sp-cart" id="sp-cart" role="dialog" aria-modal="true" aria-labelledby="sp-cart-title" aria-hidden="true" hidden>
      <div class="sp-cart-header"><div><span class="sp-section-eyebrow">IMSFRANE SHOP</span><h2 id="sp-cart-title">{e(t["cart"])}</h2></div><button class="sp-cart-close" id="sp-cart-close" type="button" aria-label="{e(t["close"])}"><i class="fa-solid fa-xmark" aria-hidden="true"></i></button></div>
      <div class="sp-cart-list" id="sp-cart-list"><p class="sp-cart-empty">{e(t["cartEmpty"])}</p></div>
      <div class="sp-cart-footer"><div class="sp-cart-total"><span>{e(t["subtotal"])}</span><strong id="sp-total">0 MAD</strong></div><p>{e(t["cartHint"])}</p>
        <button id="sp-checkout" class="sp-checkout" type="button" disabled><i class="fa-brands fa-whatsapp" aria-hidden="true"></i>{e(t["checkout"])} <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></button></div>
    </aside>
    <div id="sp-toast" class="sp-toast" role="status" aria-live="polite" hidden></div>
    <button type="button" id="sp-mobile-cart" class="sp-mobile-cart"><i class="fa-solid fa-basket-shopping" aria-hidden="true"></i><span>{e(t["viewCart"])}</span><b id="sp-mobile-count">0</b></button>
    </main>'''

def build(root):
    catalog_json=json.dumps(CATALOG,ensure_ascii=False).replace("</","<\\/")
    for lang in ("fr","en"):
        target=root/lang/"store.html"
        original=target.read_text(encoding="utf-8")
        logo_re=r'<img\b[^>]*data-cms-image="store-i(?:1|10)"[^>]*>'
        logos_before=re.findall(logo_re,original,flags=re.I)
        if len(logos_before)!=2:
            raise RuntimeError('Original shop brand logos missing')
        new_main=render(lang)
        updated,n=re.subn(r'<main\b[^>]*>[\s\S]*?</main>',lambda m:new_main,original,count=1,flags=re.I)
        if n!=1:
            raise RuntimeError('Original shop main element not found')
        updated=updated.replace("</head>",'<link rel="stylesheet" href="../store-pro.css"></head>',1)
        updated=updated.replace("</body>",'<script type="application/json" id="spCatalog">'+catalog_json+'</script><script defer src="../store-pro.js"></script></body>',1)
        updated=re.sub(r'<link\b[^>]*\bas="image"[^>]*>', '',updated,flags=re.I)
        if re.findall(logo_re,updated,flags=re.I)!=logos_before:
            raise RuntimeError('Shop brand logo changed; aborting publish')
        target.write_text(updated,encoding="utf-8")

if __name__=="__main__":
    build(Path("public"))
