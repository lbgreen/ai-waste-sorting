# Korean waste sorting: rules, exceptions and engineering mappings

Research cutoff and access date: **2026-11-09**. This covers information available by that date, not future November publications. **Verified guidance** is attributed to official sources below. **Engineering mappings and camera judgments are recommendations**, not government classifications or experimentally validated capabilities. Read the [item CSV](korean_waste_items.csv) with this document; it is a research reference, not executable rules.

## Scope and authority

South Korea does not have a universal three-stream PAPER/RECYCLING/GENERAL system. The national information service distinguishes paper, beverage cartons, clear PET bottles, several plastic streams, metal, container glass, batteries, lighting and electronics, alongside ordinary, noncombustible, food, bulky and hazardous waste. These categories have different collection routes. [Official classification hierarchy](https://www.wasteguide.or.kr/front/summary/classificationSystem.do).

Use national guidance to establish the material/stream distinction, then resolve **actual collection arrangements** through the municipality and building/collector. The national service itself supplies locality-specific information; it is guidance rather than a substitute for every local collection rule. A university may use institutional waste contracts rather than the household arrangements summarized here. No campus or collection contract has been identified. [Service scope](https://www.wasteguide.or.kr/front/summary/introductionWebsite.do).

| Source | Date verified | Applicability / limitation |
|---|---|---|
| [분리의정석 paper guidance](https://www.wasteguide.or.kr/front/dischargeMethod/typeItemHtml.do) and item dictionary | Accessible at cutoff; displayed update date not established | National information baseline; dictionary expressly defers to local methods |
| [Suwon recycling instructions](https://www.suwon.go.kr/sw-www/deptHome/dep_env/env_03/env_03_09.jsp) | Page revision **2026-07-07** | Suwon example; do not assume this is the campus collector's contract |
| [Gwanak recycling instructions](https://www.gwanak.go.kr/site/gwanak/07/10703010200002016051206.jsp) | Page revision **2026-09-16** | Gwanak example; apartment management arrangements can differ |
| [Ministry carton announcement](https://www.mcee.go.kr/home/web/board/read.do?boardId=1892240&boardMasterId=939&menuId=10598) | Published **2026-09-21** | Planned carton separation expansion for covered apartment buildings; not all premises |
| [Ministry public explainer](https://www.korea.kr/multi/visualNewsView.do?newsId=148973308) | Published **2026-10-13** | Confirms October 2026 voluntary start and January 2027 full implementation schedule |
| [Dobong disposal instructions](https://www.dobong.go.kr/subsite/waste/Contents.asp?code=10007358) | Page accessed at cutoff; exact revision not verified | Additional local exception evidence; not a national rule |
| [National administrative guideline portal](https://www.law.go.kr/행정규칙/재활용가능자원의분리수거등에관한지침) | Portal reached; substantive current text did not render | Latest promulgated amendment/effective text not independently verified; do not treat press announcements as enacted text |

A search-engine crawl date is not an effective date. Living pages may change; record the source revision and retain a permitted snapshot when the implementation profile is approved. The bibliography records access limitations rather than silently claiming that inaccessible legislation was checked.

The ministry's **2026-886 administrative notice**, dated September 23 and registered September 28, identifies the existing guideline as Ministry Directive **18, 2026-01-01**. Its proposed changes include making cartons a separate listed item, using 일반팩 terminology, replacing the drying instruction with opening/flattening, consultation over local departures, and battery-device collection advice. Comments closed October 14. This verifies a **proposal**, not final promulgation; older drying instructions in the CSV are source-specific preparation guidance, not a claim that the proposed wording is already law. [Official amendment notice](https://www.mcee.go.kr/home/web/board/read.do?boardCategoryId=&boardId=1894530&boardMasterId=827&decorator=&maxIndexPages=10&maxPageItems=10&menuId=10557&orgCd=&pagerOffset=0&searchKey=&searchValue=).

## Significant 2026 update: cartons

The ministry announced voluntary advance implementation from **October 2026**, followed by planned mandatory separation from **2027-01-01** for buildings subject to mandatory apartment management (including the specified 300-household criterion). The September announcement says the relevant guideline will be amended. It does **not** establish that every Korean household or campus already had that new mandate in November 2026. [Ministry announcement](https://www.mcee.go.kr/home/web/board/read.do?boardId=1892240&boardMasterId=939&menuId=10598), [October explainer](https://www.korea.kr/multi/visualNewsView.do?newsId=148973308).

The project should preserve cartons as a distinct recognized stream now. An ordinary milk carton and an aseptic soy-milk carton are both carton candidates, not ordinary cardboard. Whether a collection point separates 일반팩 and 멸균팩 must be resolved locally. A 2025 official local poster explains both and preparation; Paju's October 2026 notice explicitly warns against remixing collected cartons with wastepaper. [Goesan poster](https://www.goesan.go.kr/DATA/bbs/251/82D143B9-AC3B-5E9A-B99A-CDC9EC894078.pdf), [Paju notice](https://m.paju.go.kr/user/environment_07/board/BD_board.view.do?bbsCd=2001&q_ctgCd=1009&seq=20261001172143355).

## Mapping policy for this project

| Internal stream | Engineering destination | Required restriction |
|---|---|---|
| Accepted ordinary paper/cardboard | PAPER → `paper` | Prepared and permitted by site; cardboard/other-paper separation may still be required downstream |
| Accepted nonpaper packaging | RECYCLING → `recycling` | Only material combinations the collector accepts, or a documented supervised downstream separation process |
| Verified ordinary nonrecyclable waste | GENERAL → `general` | Positive rule match for READY; uncertainty fallback is a separate operating policy, not a legal label |
| Separate clear drink-PET collection | `unsupported` by default | Do not merge into mixed recycling merely because PET is recyclable |
| Cartons, batteries, lamps, electronics, food, medicines, bulky waste, hazardous waste | `unsupported` | Explain correct external route; no flap command |
| Uncertain identity/material/inferred disposal category | `unknown` / `manual_review` → UNSURE/general | Usable scene, no confirmed conflict and no explicit rule blocker; retain uncertainty warning |
| Missing/conflicting site rule or known unmet preparation | ERROR_RULE | No command; resolve explicit rule blocker |

All nominal PAPER/RECYCLING/GENERAL mappings in the CSV are **conditional on a reviewed site profile and verified prerequisites**. The CSV's `default_internal_state` distinguishes `candidate` from `manual_review` and `unsupported`; `candidate` is not permission to actuate. A clean glass bottle may be a recyclable material yet remain excluded from an initial prototype because breakage handling has not been designed.

## Material and preparation decisions

### Ordinary paper and cardboard

The national paper guidance includes corrugated board, newspaper, paperboard, books/office paper and paper cups. It excludes thermal receipts, shipping labels, baking paper and certain coated paper. Remove other materials and keep accepted paper free of water/foreign matter. Double-sided coatings that prevent tearing are an exclusion in that guidance. The visual impression of gloss alone is not a sufficient coating test. [National paper guidance](https://www.wasteguide.or.kr/front/dischargeMethod/typeItemHtml.do), [official paper explainer, historical context](https://www.korea.kr/news/policyNewsView.do?newsId=148890467).

For engineering purposes, separate **dry clean**, **wet but potentially recoverable**, **removable food residue**, **persistent grease/contamination**, and **unknown**. Do not infer a universal wet-paper rejection rule: drying and reassessment may restore eligibility. Nor should a stain detector decide that an entire pizza box is unrecyclable; clean and soiled portions may require separate inspection. If contamination cannot be removed, applicable municipal guidance may require ordinary waste. This is a preparation decision, not merely a material class. [Dobong preparation guidance](https://www.dobong.go.kr/subsite/waste/contents.asp?code=10007367).

### Cups, cartons and food packaging

**Clean paper cups are not automatically GENERAL.** National paper guidance includes them; Suwon gives preparation instructions for cups/cartons while distinguishing carton collection. A paper cup with a removable plastic lid must be separated before classification of its components. Ordinary cup acceptance, double-sided coating exceptions and return/deposit routes must be part of the site profile. [National paper guidance](https://www.wasteguide.or.kr/front/dischargeMethod/typeItemHtml.do), [Suwon](https://www.suwon.go.kr/sw-www/deptHome/dep_env/env_03/env_03_09.jsp).

The current official **paper noodle cup** dictionary entry says that an emptied, rinsed, clean paper container belongs with other paper, subject to local differences. Do not copy older blanket online advice that all noodle cups are general waste. Persistent food contamination or an unidentified laminated product still needs review. A foam noodle cup is a different material case, not covered by the paper entry. [Specific official item](https://www.wasteguide.or.kr/front/dischargeMethod/dictionaryView.do?niIdx=406), [FAQ dated 2024-09-20](https://xn--oy2b29bd3a601b.kr/front/viewAritcle.do?bbsId=BBS_0002&nttId=1308).

Cartons have a separate route despite their paper exterior. Empty, rinse, flatten/open as instructed, dry, and separate accessories. Aseptic multilayer construction does not by itself make a carton GENERAL. [Official carton poster](https://www.goesan.go.kr/DATA/bbs/251/82D143B9-AC3B-5E9A-B99A-CDC9EC894078.pdf).

Thermal receipts and used tissues are different from ordinary office paper. The former's chemistry is not reliably visible; an object-level receipt prediction still needs product/printing evidence when uncertain. Food-contact packaging likewise needs its construction and preparation assessed. [Suwon exclusions](https://www.suwon.go.kr/sw-www/deptHome/dep_env/env_03/env_03_09.jsp), [Dobong exclusions](https://www.dobong.go.kr/subsite/waste/Contents.asp?code=10007358).

### Plastic bottles, containers, caps, labels and film

Clear **water/beverage PET bottles** have a separate collection route. Suwon instructs emptying/rinsing, label removal, compression and closing the cap. This differs from a simplistic “always remove every cap” rule. Other plastic containers, including colored PET, use the applicable plastic stream and removal of foreign-material attachments. Transparent appearance alone does not identify PET, and not every transparent PET tray is a beverage bottle. [Suwon](https://www.suwon.go.kr/sw-www/deptHome/dep_env/env_03/env_03_09.jsp), [Gwanak](https://www.gwanak.go.kr/site/gwanak/07/10703010200002016051206.jsp), [Hwaseong PET separation](https://h-waste.hscity.go.kr/05_recycle/05_recycle0101.asp).

Clean accepted film packaging can be recyclable, including relevant snack/noodle wrappers. “OTHER” is not synonymous with GENERAL: composite packaging may have an accepted film route. Conversely, a recycling symbol does not authorize dirty contents or mixed components. If cleaning cannot remove residue, follow the local exception; otherwise request preparation first. Do not classify bioplastic/compostable-looking items into conventional plastics based on shape. Unverified PLA or resin identity remains an uncertain legal/material label; the operating policy may route it to general with UNSURE, without declaring that route legally verified. [Suwon film guidance](https://www.suwon.go.kr/sw-www/deptHome/dep_env/env_03/env_03_09.jsp), [marking system](https://www.keco.or.kr/web/lay1/S1T183C1049/contents.do).

### Metal and glass

Empty and clean accepted cans; separate nonmetal attachments. Aerosol/butane containers require residual-content handling that a webcam cannot establish, so they are unsupported in this prototype even where a municipality eventually accepts properly emptied cans. Do not instruct the machine to puncture or process them. [Gwanak can instructions](https://www.gwanak.go.kr/site/gwanak/07/10703010200002016051206.jsp).

Container glass is different from ceramics, mirrors, heat-resistant cookware and broken glass. Deposit-bearing beverage bottles have a return route. These distinctions require product identity, local handling and mechanical suitability; “looks like glass” is inadequate. Broken/noncontainer glass can require noncombustible bags or other local handling; Dobong explicitly distinguishes small wrapped fragments from other cases, illustrating why no national GENERAL shortcut is valid. [Suwon bottles](https://www.suwon.go.kr/sw-www/deptHome/dep_env/env_03/env_03_09.jsp), [Dobong exceptions](https://www.dobong.go.kr/subsite/waste/Contents.asp?code=10007358).

### Special streams and composites

Batteries/power banks, fluorescent lamps, electronics, medicines, edible food waste, reusable textiles, bulky products and hazardous residues need routes outside this simplified bin. The official hierarchy makes several of these recyclable in a broad sense, but that does not make them suitable for mixed RECYCLING. A recent Goyang notice specifically directs rechargeable-battery products away from ordinary recycling/general bags. [Classification hierarchy](https://www.wasteguide.or.kr/front/summary/classificationSystem.do), [Goyang notice, 2026-10-28](https://www.goyang.go.kr/ilsegu/user/bbs/BD_selectBbs.do?q_bbsCode=1030&q_bbscttSn=20261028102845730).

For detachable composites, classify the separated components. For inseparable composites, consult the specific item/mark and local acceptance; do not invent either “all composites GENERAL” or “all marked packages recyclable.” Example: beverage cartons have a dedicated recyclable stream, while a foil-lined insulated shipping box may be excluded from ordinary cardboard. [EPR packaging categories](https://portal.budamgum.or.kr/cmb/portal/epr/system/eprIntroduce.do?tp=05), [Suwon cardboard exclusions](https://www.suwon.go.kr/sw-www/deptHome/dep_env/env_03/env_03_09.jsp).

## What the webcam cannot prove

These are engineering limitations to test, not claims of measured camera performance:

- Interior liquid, underside residue, invisible grease and whether contamination is removable.
- PE/PLA/PET or multilayer composition solely from transparency, color or shape.
- Thermal chemistry, coatings on unseen surfaces, or tiny/unreadable component markings.
- Whether a gas container is depressurized, electronics contain a battery, or a sharp edge is hidden.
- Municipality, deposit eligibility, building contract or downstream collector acceptance without configured metadata.

OCR, multiple views, verified product lookup and operator checks can supply additional evidence, but the system should state where that evidence came from. Confidence in recognizing “cup” must not be displayed as confidence that the cup satisfies the disposal rule.

## Item reference and conflict handling

[korean_waste_items.csv](korean_waste_items.csv) contains more than 30 everyday items with bilingual names, material, official category, preparation, exceptions, conditional engineering mapping, camera assessment, locality/date and direct official URL. Conditions are deliberately part of the item definition: a clean food container and a heavily soiled one are distinct decision cases.

When sources differ, first check **jurisdiction**, **object subtype**, **publication/effective date**, and **collection availability**. Gwanak's broad paper grouping is not proof that cartons can be physically mixed with ordinary paper everywhere. The 2021 paper explainer is historical context, not authority to override the current specific noodle-cup entry. If a current local source and a national item page cannot be reconciled, disable the automatic rule and obtain site clarification in Phase 2. No special item is to be silently downgraded to GENERAL.

## Multi-item extension

Apply this reference to **each visible instance** before batch aggregation. Two different **confident** supported destinations produce `ERROR_MIXED_WASTE`, even when another item is uncertain. Otherwise a usable scene with uncertain identification/inferred disposal category produces `UNSURE` with command `general`; all confident items sharing a category produce `READY` with that category. Fallback general must not create a false confirmed-category conflict.

Known unsupported streams remain blocked; unresolved count/occlusion produces `WARNING_DETECTION` with no command. Explicit missing/conflicting site rules or known unmet preparation remain rule blockers. These preserve Korean disposal rules while changing the operating fallback for uncertain classifications. The CSV retains official/reference labels and internal uncertainty reasons, not the new batch event policy. Its `manual_review` entries must be interpreted by reason, not automatically converted or rejected en masse. [Architecture](04_system_architecture.md) defines the complete decision order.

The fallback is user-directed and is not a government rule: an unknown object may actually require recycling or separate collection. Keep its official stream unknown, record `assignment_basis=uncertainty_fallback`, and measure the resulting disposal errors rather than relabeling the ground truth as GENERAL.
