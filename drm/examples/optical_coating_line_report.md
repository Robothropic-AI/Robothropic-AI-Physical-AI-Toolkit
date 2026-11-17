# Deployment Readiness Report: Anti-reflective coating of optical lenses, batch vacuum deposition line

**Status: PROVISIONAL.** The process model has not been approved by a named person; open questions remain.

Human oversight constraint: mandatory. Wording generated from the scores by plain templates; no language-model narrative. Abbreviations are explained in the glossary at the end.

## Executive summary

This is a provisional analysis of 'Anti-reflective coating of optical lenses, batch vacuum deposition line' covering 10 stages. Tier 1 starting points, by the ranking formula: 1 (Incoming inspection), 4 (Recipe selection). No appropriate AI role was found for: 7 (Venting and unloading). Low-confidence analyses, which depend on open questions: 5 (Chamber loading and pump-down), 6 (Deposition run), 8 (Optical QC), 10 (Disposition and records). Scores are model judgments for engineer review; see the limitations.

## Priority map

Tiers and order come from a deterministic formula (weights uncalibrated); tier 1 means start here.

| Tier | Stage | AI role | Fit | Effort | Worst severity | Human check | Layer | Confidence | Why |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1. Incoming inspection | perception | 4 | 3 | 3 | review_after | fast | medium | Tier 1: fit 4/5, effort 3/5, worst-case severity 3/5 (partial), human check review_after, confidence medium. |
| 1 | 4. Recipe selection | reasoning | 4 | 2 | 4 | approve_before | slow | medium | Tier 1: fit 4/5, effort 2/5, worst-case severity 4/5 (partial), human check approve_before, confidence medium. |
| 2 | 2. Ultrasonic cleaning | reasoning | 3 | 3 | 3 | approve_before | slow | medium | Tier 2: fit 3/5, effort 3/5, worst-case severity 3/5 (partial), human check approve_before, confidence medium. |
| 2 | 3. Drying and fixturing | perception | 3 | 3 | 3 | review_after | slow | medium | Tier 2: fit 3/5, effort 3/5, worst-case severity 3/5 (partial), human check review_after, confidence medium. |
| 2 | 5. Chamber loading and pump-down | perception | 3 | 3 | 3 | review_after | fast | low | Tier 2: fit 3/5, effort 3/5, worst-case severity 3/5 (partial), human check review_after, confidence low. |
| 2 | 8. Optical QC | reasoning | 4 | 2 | 4 | approve_before | slow | low | Tier 2: fit 4/5, effort 2/5, worst-case severity 4/5 (irreversible), human check approve_before, confidence low. |
| 3 | 9. Cosmetic inspection | perception | 4 | 3 | 4 | approve_before | slow | medium | Tier 3: fit 4/5, effort 3/5, worst-case severity 4/5 (irreversible), human check approve_before, confidence medium. |
| 3 | 10. Disposition and records | reasoning | 3 | 3 | 4 | approve_before | slow | low | Tier 3: fit 3/5, effort 3/5, worst-case severity 4/5 (irreversible), human check approve_before, confidence low. |
| 3 | 6. Deposition run | perception | 3 | 4 | 4 | approve_before | slow | low | Tier 3: fit 3/5, effort 4/5, worst-case severity 4/5 (irreversible), human check approve_before, confidence low. |
| 3 | 7. Venting and unloading | none | 1 | 1 | 3 | human_only | human_only | medium | No AI role: Venting, cooling and unloading are physical handling steps with little decision content. Any AI role would be marginal, so none is appropriate. |

## Stage details

### 1. Incoming inspection

**AI role:** perception (also communication), fit 4/5. Camera-based defect detection for scratches, chips and contamination is well-defined and checkable. The operator keeps the accept/reject judgment and the AI drafts the log entry.

**Integration:** effort 3/5, latency near_realtime, human check review_after. New imaging hardware and a labelled defect dataset must be collected. The log system is not named, so a lightweight record integration is needed.
- Data required: Labelled images of substrate defects by type; Lot numbers; Defect acceptance criteria; Historical inspection findings
- Interfaces: Inspection camera and lighting station; Lot log or record system (currently unspecified); Operator review screen

**Risks** (regulatory exposure 2/5: General quality-system and record expectations for the lot log.)
- A missed substrate defect (scratch or chip) passes into the line and is only discovered after coating, wasting a coating run on bad substrates. (severity 3/5, partial)
- Over-rejection of acceptable substrates causes unnecessary scrap or delay. (severity 2/5, reversible)

**Assumptions:** Defect acceptance criteria exist and can be written down; Substrates can be imaged at the inspection point; The lot log is a paper or simple digital record

*Layer: fast. Confidence: medium.*

### 2. Ultrasonic cleaning

**AI role:** reasoning (also communication), fit 3/5. AI could recommend the cleaning recipe from lot data and flag mismatches, while the operator does the physical loading and runs the line. Selection is a bounded sub-task.

**Integration:** effort 3/5, latency batch, human check approve_before. Recommendation is advisory, but reading line parameters needs one system integration whose interface is not stated.
- Data required: Cleaning recipe library; Lot data and substrate type from stage 1; Cleaning line parameters and alarms; Past cleaning outcomes
- Interfaces: Cleaning line controller or recipe selector (interface unknown); Lot record; Operator display

**Risks** (regulatory exposure 2/5: General quality-system and record expectations for recipe records.)
- A wrong cleaning recipe recommendation that is not caught leaves contamination or damages substrates, causing coating adhesion or cosmetic failures found later. (severity 3/5, partial)

**Assumptions:** Cleaning recipes are stored digitally or can be digitised; The line exposes parameters through a PLC or export; Rework lots re-entering here may need a different recipe

*Layer: slow. Confidence: medium.*

### 3. Drying and fixturing

**AI role:** perception (also communication), fit 3/5. A camera could verify fixture loading and capture substrate positions automatically for the record. Mounting in a laminar-flow area is manual work that stays with the operator.

**Integration:** effort 3/5, latency near_realtime, human check review_after. New camera capture in a cleanliness-controlled area and a position-record integration are required.
- Data required: Fixture and dome layout; Images of loaded fixture; Substrate-to-position mapping; Lot identifiers
- Interfaces: Camera in or near the laminar-flow area; Position record system (unspecified); Operator confirmation screen

**Risks** (regulatory exposure 3/5: Position records support traceability and may be audited or customer-mandated.)
- Incorrect position record misattributes substrates to dome positions, undermining traceability and later root-cause analysis. (severity 3/5, partial)
- Added equipment or handling in the laminar-flow area introduces particulate contamination. (severity 3/5, partial; not detectable before harm)

**Assumptions:** Position recording is currently manual; Customers expect traceability from lot to dome position; Camera placement does not disturb laminar flow

*Layer: slow. Confidence: medium.*

### 4. Recipe selection

**AI role:** reasoning (also communication), fit 4/5. Matching a recipe from the library against the customer specification is digital and checkable. AI can propose and cross-check, while the process engineer remains accountable for confirmation.

**Integration:** effort 2/5, latency batch, human check approve_before. Data is digital, but the recipe library and specification formats need extraction and cleaning.
- Data required: Recipe library with layer materials, thicknesses and rates; Customer specifications; Recipe revision history; Lot and product mapping
- Interfaces: Recipe library (system unspecified); Customer specification documents; Engineer approval interface

**Risks** (regulatory exposure 3/5: Customer-mandated controls and recipe traceability are likely, but no regulation is named in the model.)
- A wrong or outdated recipe is confirmed against the specification, so a full run is coated incorrectly and defective lenses may reach the customer. (severity 4/5, partial)
- Misreading the customer specification leads to a mismatch that is detected only at optical QC. (severity 3/5, partial)

**Assumptions:** Specifications are available as text or structured documents; Recipe library has version control; The ambiguity on how many confirmations occur before deposition is unresolved

*Layer: slow. Confidence: medium.*

### 5. Chamber loading and pump-down

**AI role:** perception (also communication), fit 3/5. AI could monitor pump-down curves, flag leaks or abnormal pumping behaviour and predict time to base pressure. Loading the dome and starting pump-down remain manual.

**Integration:** effort 3/5, latency near_realtime, human check review_after. Read-only data capture from the pumping system is one integration. No control authority is assumed.
- Data required: Pressure and pump-down history; Pump and valve status; Base pressure target; Past pump-down curves for baselining
- Interfaces: Vacuum gauge and pumping system data (PLC or historian); Read-only monitoring dashboard; Operator alerts

**Risks** (regulatory exposure 2/5: General quality-system and record expectations.)
- A missed leak or abnormal pump-down signal lets a run start with poor vacuum, degrading coating quality across the lot. (severity 3/5, partial)
- Nuisance alerts delay the process and cause alarm fatigue. (severity 1/5, reversible)

**Assumptions:** Pressure data is available electronically; Base pressure target is defined, though the model leaves it unspecified; AI role is advisory only, with no control of valves or pumps

*Layer: fast. Confidence: low.*

### 6. Deposition run

**AI role:** perception (also reasoning, communication), fit 3/5. AI could watch rate, thickness and optical monitor signals for drift or deviation and alert the operator. Control and abort authority stay with the PLC and operator.

**Integration:** effort 4/5, latency near_realtime, human check approve_before. Several systems and real-time data limits are involved. Read-only monitoring avoids safety-rated control, but data access and calibration are substantial. Because a missed deviation or a wrong abort is irreversible, any AI recommendation to continue or abort needs operator approval before action.
- Data required: Quartz crystal monitor readings; Optical monitor spectra; PLC shutter and rate states; E-beam and ion-assist parameters; Historical runs with outcomes
- Interfaces: PLC data export or OPC-style gateway (unspecified); Quartz and optical monitor outputs; Operator alert interface

**Risks** (regulatory exposure 3/5: Run data may be needed for batch traceability, but the model names no regulation.)
- A missed deviation allows a mis-thickness or contaminated coating to complete, losing the production run or letting a defect reach the customer. (severity 4/5, irreversible; not detectable before harm)
- A false alarm prompts an unnecessary operator abort and wastes a run. (severity 4/5, irreversible)

**Assumptions:** PLC and monitors can export data at useful rates; AI has no write access to the PLC, shutters or e-beam; Handling of aborted runs is unresolved in the model

*Layer: slow. Confidence: low.*

### 7. Venting and unloading

**AI role:** none, fit 1/5. Venting, cooling and unloading are physical handling steps with little decision content. Any AI role would be marginal, so none is appropriate.

**Integration:** effort 1/5, latency batch, human check human_only. No AI integration is proposed. Chamber data could be logged but the stage adds little value.

**Risks** (regulatory exposure 1/5)
- Mishandling during unloading chips or scratches coated lenses, or venting too early thermally shocks substrates. (severity 3/5, irreversible; not detectable before harm)

**Assumptions:** Venting is a standard automated or manual chamber sequence; Cooling criteria are fixed by procedure

*Layer: human_only. Confidence: medium.*

### 8. Optical QC

**AI role:** reasoning (also perception, communication), fit 4/5. Spectrophotometer data is digital, and comparing reflectance against a specification is well-defined and checkable. AI can compute pass or fail and flag borderline results for a person to confirm.

**Integration:** effort 2/5, latency batch, human check approve_before. Instrument output is digital and an export likely exists. Linking witness samples to runs is unresolved and may need new data capture.
- Data required: Spectrophotometer reflectance measurements; Reflectance specification limits; Witness sample identity and run linkage; Historical measurements
- Interfaces: Spectrophotometer data export or API; Specification record; QC reviewer interface

**Risks** (regulatory exposure 3/5: Customer-mandated QC records and traceability are likely; no regulation is named.)
- A false pass on out-of-specification reflectance releases defective lenses to the customer. (severity 4/5, irreversible)
- A false fail sends good lots to rework or scrap, costing time and material. (severity 3/5, partial)

**Assumptions:** The model names no actor for this stage, so a QC technician or engineer is assumed to supervise; Witness samples are linked to the lot, though the origin of witness samples is unresolved; Measurement is already digital

*Layer: slow. Confidence: low.*

### 9. Cosmetic inspection

**AI role:** perception (also communication), fit 4/5. Machine vision under controlled lighting can detect pinholes, haze and stains and assist the operator. Findings are visual and checkable, but defect criteria need to be collected.

**Integration:** effort 3/5, latency near_realtime, human check approve_before. New imaging hardware, controlled lighting and labelled data collection are required. Haze and stains can be hard to image reliably. Because a missed defect reaching the customer is irreversible, the operator approves each accept decision before lenses move on.
- Data required: Labelled images of pinholes, haze and stains; Cosmetic acceptance criteria; Lens identifiers; Operator disposition on flagged items
- Interfaces: Imaging station replacing or augmenting the inspection lamp; Findings record; Operator review screen

**Risks** (regulatory exposure 2/5: General quality-system and record expectations; customer cosmetic standards may apply.)
- A missed cosmetic defect on a coated lens reaches the customer. (severity 4/5, irreversible)
- Over-flagging increases rework or scrap and slows throughput. (severity 2/5, reversible)

**Assumptions:** Cosmetic criteria are defined, though the model does not specify them; Whether a cosmetic failure triggers rework or scrap is unresolved; The 4 rating assumes the human gives the final accept on AI findings

*Layer: slow. Confidence: medium.*

### 10. Disposition and records

**AI role:** reasoning (also communication), fit 3/5. AI can compile QC results into the batch record, check completeness and recommend release, rework or scrap. The decision and accountability for release stay with a person.

**Integration:** effort 3/5, latency batch, human check approve_before. Several records must be consolidated into the batch record, whose system is not named. The disposition decision and its criteria are unresolved.
- Data required: Optical QC result; Cosmetic inspection findings; Lot and run records; Rework history and scrap criteria; Batch record template
- Interfaces: Batch record system (unspecified); QC and inspection data sources; Quality engineer approval interface

**Risks** (regulatory exposure 3/5: The batch record is kept for traceability, which suggests audited records or customer-mandated controls; no regulation is named.)
- Wrongly releasing a failing lot sends defective lenses to the customer. (severity 4/5, irreversible)
- Incomplete or incorrect batch record breaks traceability for audit or complaint investigation. (severity 3/5, partial)
- Wrong rework versus scrap choice wastes a recoverable lot or sends an unrecoverable lot through strip and recoat. (severity 3/5, partial)

**Assumptions:** The model names no actor, so a quality engineer is assumed to be accountable; Rework and scrap criteria are unresolved; Rework path returns to stage 2 as stated

*Layer: slow. Confidence: low.*

## Cross-cutting risks

- Severe failure modes (severity 4 or more) occur at stages 4 (Recipe selection), 6 (Deposition run), 8 (Optical QC), 9 (Cosmetic inspection), 10 (Disposition and records); a human check is needed before AI output takes effect there.
- Audited records or customer-mandated controls (regulatory exposure 3 or more) apply at stages 3 (Drying and fixturing), 4 (Recipe selection), 6 (Deposition run), 8 (Optical QC), 10 (Disposition and records).
- Stages 5 (Chamber loading and pump-down), 6 (Deposition run), 8 (Optical QC), 10 (Disposition and records) rest on unresolved questions, so their scores may change.

## Open questions for the partner

1. Where and when are witness samples loaded, and which stage produces them?
2. How many recipe confirmations take place before deposition, and who performs each?
3. Who performs the optical QC measurements and the disposition decision (operator, QC technician, quality engineer)?
4. What is the base pressure target and who confirms it has been reached?
5. Who decides between rework and scrap for failing lots, and on what criteria?
6. Does a cosmetic inspection failure also trigger rework or scrap, or only optical QC failures?
7. Can cosmetic inspection (stage 9) run in parallel with optical QC (stage 8)?
8. Where is the strip step performed, and does stripped material re-enter at stage 1 or stage 2?
9. What happens to a run aborted by the operator in stage 6 (partial coating, rework, scrap)?
10. Which records does the batch record contain, and in which system is it kept?

## Limitations

- Scores are judgments made by a language model on anchored 1-5 scales, applied to a process description written by people. They are a structured starting point for review by a process engineer, not measurements.
- The priority tiers come from a simple formula (fit minus effort minus worst-case severity, with a penalty for irreversible failures). Its weights are not calibrated against real deployments. It has no benefit term, so it ranks feasibility and risk and not value. It gives no credit for human oversight and ignores the analyst's confidence.
- The analysis shows where AI could act. It does not size benefits, cost or schedule, and it does not validate any design.
- Accountability for the process, the safety envelope, quality obligations and the decision to deploy stays with the process owner.
- This analysis is PROVISIONAL: the process model has not been approved by a named person, and the open questions listed in this report remain to be resolved.
- Human oversight constraint applied: mandatory.
- Provenance: Analyst reply from a manual run; one stray empty field removed by hand.

## Glossary

General definitions of the abbreviations used in this report. A plant may use some of these terms more specifically.

- **AI**: Artificial intelligence: software that performs tasks that normally need human judgment, such as recognising defects in images or recommending a setting.
- **API**: Application programming interface: a defined way for one software system to request data from, or send data to, another.
- **OPC**: A family of industrial standards for exchanging data between control equipment and software (originally 'OLE for Process Control').
- **PLC**: Programmable logic controller: a rugged industrial computer that runs a machine's control sequences, such as opening shutters or holding a deposition rate.
- **QC**: Quality control: checks that a product or batch meets its specification, such as measuring or inspecting samples.

---
*Generated by the Robothropic AI Deployment Readiness Mapper.*


