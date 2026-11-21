# Deployment Readiness Report: Anti-reflective coating of optical lenses, batch vacuum deposition line

**Status: PROVISIONAL.** The process model has not been approved by a named person; open questions remain.

Human oversight constraint: mandatory. Wording generated from the scores by plain templates; no language-model narrative. Abbreviations are explained in the glossary at the end.

## Executive summary

This is a provisional analysis of 'Anti-reflective coating of optical lenses, batch vacuum deposition line' covering 10 stages. Tier 1 starting points, by the ranking formula: 1 (Incoming inspection), 4 (Recipe selection), 8 (Optical QC). No appropriate AI role was found for: 7 (Venting and unloading). Low-confidence analyses, which depend on open questions: 5 (Chamber loading and pump-down), 6 (Deposition run), 8 (Optical QC), 10 (Disposition and records). Scores are model judgments for engineer review; see the limitations.

## Priority map

Tiers and order come from a deterministic formula (weights uncalibrated); tier 1 means start here.

How to read the columns: *Layer* says where an AI action would sit. *fast* means onboard or real-time, low-stakes and reversible; *slow* means verified and human-reviewed, higher-stakes; *human_only* means no AI action is proposed. *AI role: none* means the same: it does not mean the stage cannot be improved by other means, such as classical automation or robotics, which this analysis does not assess.

| Tier | Stage | AI role | Fit | Effort | Worst severity | Human check | Layer | Confidence | Why |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1. Incoming inspection | perception | 4 | 3 | 3 | review_after | slow | medium | Tier 1: fit 4/5, effort 3/5, worst-case severity 3/5 (partial), human check review_after, confidence medium. |
| 1 | 4. Recipe selection | reasoning | 4 | 2 | 4 | approve_before | slow | medium | Tier 1: fit 4/5, effort 2/5, worst-case severity 4/5 (partial), human check approve_before, confidence medium. |
| 1 | 8. Optical QC | reasoning | 4 | 2 | 4 | approve_before | slow | low | Tier 1: fit 4/5, effort 2/5, worst-case severity 4/5 (partial), human check approve_before, confidence low. |
| 2 | 9. Cosmetic inspection | perception | 4 | 3 | 4 | approve_before | slow | medium | Tier 2: fit 4/5, effort 3/5, worst-case severity 4/5 (partial), human check approve_before, confidence medium. |
| 3 | 2. Ultrasonic cleaning | reasoning | 3 | 3 | 3 | approve_before | slow | medium | Tier 3: fit 3/5, effort 3/5, worst-case severity 3/5 (partial), human check approve_before, confidence medium. |
| 3 | 3. Drying and fixturing | perception | 3 | 3 | 3 | review_after | slow | medium | Tier 3: fit 3/5, effort 3/5, worst-case severity 3/5 (partial), human check review_after, confidence medium. |
| 3 | 5. Chamber loading and pump-down | perception | 3 | 3 | 3 | review_after | slow | low | Tier 3: fit 3/5, effort 3/5, worst-case severity 3/5 (partial), human check review_after, confidence low. |
| 3 | 6. Deposition run | perception | 3 | 4 | 4 | approve_before | slow | low | Tier 3: fit 3/5, effort 4/5, worst-case severity 4/5 (partial), human check approve_before, confidence low. |
| 3 | 7. Venting and unloading | none | 1 | 1 | 3 | human_only | human_only | medium | No AI role: Venting, cooling and unloading are physical handling tasks with no meaningful AI role. At most, a vent and cool-down log could be captured, but that adds little value. |
| 3 | 10. Disposition and records | reasoning | 3 | 3 | 4 | approve_before | slow | low | Tier 3: fit 3/5, effort 3/5, worst-case severity 4/5 (partial), human check approve_before, confidence low. |

## Stage details

### 1. Incoming inspection

**AI role:** perception (also communication), fit 4/5. Machine-vision inspection of substrates for scratches, chips and contamination is a well-defined, checkable perception task. The AI flags candidates and drafts the log entry while the operator confirms the disposition.

**Integration:** effort 3/5, latency near_realtime, human check review_after. New data capture (cameras, lighting) is needed and a labelled defect dataset must be collected. The process model names no existing system, so the findings log would need a digital capture path.
- Data required: Labelled images of acceptable and defective substrates (scratches, chips, contamination); Lot number; Operator findings log entries
- Interfaces: Not specified in the source. Options: new camera and lighting station with image capture software; manual or digital entry into the lot findings log.

**Risks** (regulatory exposure 2/5: General quality-system and record expectations apply to the lot log. The process model names no specific regulation.)
- AI misses a scratch or chip so a defective substrate proceeds into cleaning and coating. (severity 3/5, partial)
- False positives cause good substrates to be held back, delaying the lot. (severity 1/5, reversible)

**Assumptions:** Inspection is analysed as an AI-assisted camera station, with the operator reviewing flagged and sampled results after the fact.; The findings log is currently a manual or paper record because no system is named.

*Layer: slow. Confidence: medium.*

### 2. Ultrasonic cleaning

**AI role:** reasoning (also communication), fit 3/5. AI can suggest the cleaning recipe for the lot and check that recipe parameters match substrate type. Loading baskets and running the line remain physical operator tasks.

**Integration:** effort 3/5, latency batch, human check approve_before. One system integration with the multi-tank line is needed, and the interface is unknown. Historical recipe and outcome data would have to be collected to support recommendations.
- Data required: Cleaning recipe library; Lot and substrate type; Cleaning line run parameters and outcomes
- Interfaces: Not specified in the source. Options: PLC data export from the cleaning line; manual recipe entry log.

**Risks** (regulatory exposure 2/5: General quality-system and record expectations apply to recipe selection records.)
- Wrong cleaning recipe recommended and applied, leaving residue that causes coating adhesion failure or haze discovered later. (severity 3/5, partial)

**Assumptions:** The AI role analysed is a recipe recommendation that the operator approves before the run.; The cleaning line has some digital recipe selection capability, which the process model does not confirm.

*Layer: slow. Confidence: medium.*

### 3. Drying and fixturing

**AI role:** perception (also communication), fit 3/5. A camera could verify fixture loading and record substrate positions automatically, replacing manual position recording. Mounting in a laminar-flow area remains a manual, contamination-sensitive task.

**Integration:** effort 3/5, latency near_realtime, human check review_after. New camera capture in a clean area and labelled position data would be needed. Contamination control constrains where equipment can be placed.
- Data required: Images of the loaded dome; Fixture position map; Substrate position record
- Interfaces: Not specified in the source. Options: camera station in the laminar-flow area; manual entry into the position record.

**Risks** (regulatory exposure 3/5: Position records support traceability, which may be a customer-mandated control. The process model names no specific regulation.)
- Position record is wrong or lost, so a substrate cannot be traced to its location in the dome and its witness-sample correlation is unreliable. (severity 3/5, partial)
- Camera equipment or handling introduces particulate contamination into the laminar-flow area. (severity 3/5, partial)

**Assumptions:** The AI role analysed is verification and automatic logging of positions, not mounting.; Position records are currently manual because no system is named.

*Layer: slow. Confidence: medium.*

### 4. Recipe selection

**AI role:** reasoning (also communication), fit 4/5. Matching customer specification to recipe library entries is a well-defined, checkable lookup and comparison task. The AI proposes the recipe and flags mismatches, while the process engineer accepts accountability for the choice.

**Integration:** effort 2/5, latency batch, human check approve_before. The data is likely already digital, though the library format and specification format are not stated. Some cleaning of specification text is expected.
- Data required: Recipe library (materials, thicknesses, deposition rates); Customer specification; Substrate material and geometry; Historical run outcomes per recipe
- Interfaces: Not specified in the source. Options: export or API from the recipe library; document or PDF parsing of the customer specification.

**Risks** (regulatory exposure 3/5: Recipe confirmation against the customer specification is a customer-mandated control and its record is likely audited.)
- Wrong recipe is recommended and approved, so the entire lot is coated to the wrong specification and the run is lost. (severity 4/5, partial)
- Customer specification is misread or outdated, leading to a recipe that does not meet the actual requirement. (severity 4/5, partial)

**Assumptions:** The recipe library is digital and accessible, although the process model names no system for it.; A wrongly coated lot can be stripped and recoated through the declared rework path from stage 10, so the failure is partial rather than irreversible.

*Layer: slow. Confidence: medium.*

### 5. Chamber loading and pump-down

**AI role:** perception (also communication), fit 3/5. AI can monitor the pump-down curve for anomalies such as leaks or slow pumping and alert the operator. Loading the dome and starting pump-down stay with the operator.

**Integration:** effort 3/5, latency near_realtime, human check review_after. One system integration to read pressure and pump data is needed. The base pressure target and who confirms it are unresolved in the process model.
- Data required: Chamber pressure time series; Pumping system status; Base pressure target; Historical pump-down curves
- Interfaces: Not specified in the source. Options: PLC data export; OPC UA; pressure gauge analog or serial output.

**Risks** (regulatory exposure 2/5: General quality-system and record expectations apply to process parameters.)
- Anomaly such as a leak or outgassing goes undetected and the run starts at inadequate vacuum, degrading coating adhesion and optical performance. (severity 3/5, partial)
- False alarms delay pump-down confirmation and reduce throughput. (severity 1/5, reversible)

**Assumptions:** The AI role analysed is read-only monitoring and alerting with no control of the pumping system.; Pressure data is accessible digitally from the vacuum system, which the process model does not confirm.

*Layer: slow. Confidence: low.*

### 6. Deposition run

**AI role:** perception (also reasoning, communication), fit 3/5. AI can monitor rate, thickness and ion assist signals to detect drift and advise the operator to abort. Control stays with the PLC and the operator because of hard-real-time dynamics and the cost of an incorrect action.

**Integration:** effort 4/5, latency near_realtime, human check approve_before. Several systems must be read in near real time and data must be time-aligned and calibrated. Any action on the process would involve physical integration and safety review, so the analysis assumes advisory use only.
- Data required: PLC shutter and rate data; Quartz crystal monitor thickness and rate; Optical monitor signals; E-beam and ion assist parameters; Recipe layer sequence; Historical run data with QC outcomes
- Interfaces: PLC; Quartz crystal monitor; Optical monitor; Not specified in the source. Options: PLC data export; OPC UA for data readout.

**Risks** (regulatory exposure 3/5: Process records for the deposition run support traceability and may be customer-mandated.)
- AI fails to flag a deposition deviation, so the run completes out of specification and a coated lot is lost or defective. (severity 4/5, partial; not detectable before harm)
- AI advises an unwarranted abort, wasting a run partway through the layer sequence and leaving partially coated substrates. (severity 3/5, partial)
- A defective lot passes later checks and reaches the customer. (severity 4/5, partial)

**Assumptions:** The AI role analysed is advisory monitoring only, with no direct control of the PLC, shutters or e-beam.; Process data is accessible from the PLC and monitors in digital form, which the process model does not confirm.; Failed coatings can be stripped and recoated via the rework path in stage 10, so failures are partial rather than irreversible.

*Layer: slow. Confidence: low.*

### 7. Venting and unloading

**AI role:** none, fit 1/5. Venting, cooling and unloading are physical handling tasks with no meaningful AI role. At most, a vent and cool-down log could be captured, but that adds little value.

**Integration:** effort 1/5, latency batch, human check human_only. No AI integration is proposed. Any status logging would use existing data if available.
- Data required: Chamber vent and temperature status
- Interfaces: Not specified in the source. Options: PLC data export; manual log.

**Risks** (regulatory exposure 1/5)
- Substrates are unloaded before sufficient cooling or handled carelessly, causing thermal stress, damage or contamination of coated surfaces. (severity 3/5, partial)

**Assumptions:** No records are kept at this stage, as the process model lists none.

*Layer: human_only. Confidence: medium.*

### 8. Optical QC

**AI role:** reasoning (also perception, communication), fit 4/5. Comparing digital spectrophotometer reflectance data to the specification is well-defined and checkable. AI can compute the comparison, flag marginal results and draft the pass or fail result for human confirmation.

**Integration:** effort 2/5, latency batch, human check approve_before. Measurement data is already digital and an export is likely available. Effort is mainly data cleaning and linking witness samples to runs, which the process model leaves unresolved.
- Data required: Spectrophotometer reflectance spectra; Reflectance specification; Witness sample identity and run linkage; Historical QC results
- Interfaces: Spectrophotometer; Not specified in the source. Options: instrument data export (CSV or file output); vendor API.

**Risks** (regulatory exposure 3/5: Pass or fail decisions against the customer specification are likely a customer-mandated control with audited records.)
- AI wrongly passes an out-of-specification lot, so a defective lot proceeds toward release and may reach the customer. (severity 4/5, partial)
- AI wrongly fails a conforming lot, sending it unnecessarily to rework or scrap. (severity 3/5, partial)
- Witness samples are not representative of the lot or are mislinked, giving a misleading result. (severity 4/5, partial; not detectable before harm)

**Assumptions:** The AI role analysed is computing and proposing the pass or fail result, which a human approves before it takes effect.; Witness samples come from the deposition run and are traceable to the lot, although the process model leaves their origin open.; The performer of the QC measurement is unknown, as the process model lists no actor.

*Layer: slow. Confidence: low.*

### 9. Cosmetic inspection

**AI role:** perception (also communication), fit 4/5. Machine-vision detection of pinholes, haze and stains under controlled lighting is a well-defined, checkable perception task. The AI flags defects and the operator reviews and decides.

**Integration:** effort 3/5, latency near_realtime, human check approve_before. New camera capture and controlled illumination must be built around or in place of the inspection lamp. Labelled defect data must be collected, and haze detection on coated optics can be difficult.
- Data required: Labelled images of pinholes, haze and stains; Lens identity and lot number; Operator findings
- Interfaces: Inspection lamp; Not specified in the source. Options: new camera and lighting station with image capture software; manual findings log.

**Risks** (regulatory exposure 3/5: Cosmetic acceptance is typically a customer-mandated control and its records are likely audited.)
- AI misses a cosmetic defect such as haze or a pinhole, so a defective lens is released and reaches the customer. (severity 4/5, partial)
- AI over-rejects good lenses, causing unnecessary rework or scrap. (severity 2/5, partial)

**Assumptions:** Inspection is analysed as an AI-assisted camera station with the operator approving results before they take effect.; The process model does not say whether a cosmetic failure triggers rework or scrap, so only the detection step is analysed.

*Layer: slow. Confidence: medium.*

### 10. Disposition and records

**AI role:** reasoning (also communication), fit 3/5. AI can consolidate QC results, propose a release, rework or scrap recommendation and draft the batch record. The accountable disposition decision stays with a person.

**Integration:** effort 3/5, latency batch, human check approve_before. Data from several upstream stages must be consolidated, and the system holding the batch record is not named. The rework-versus-scrap criteria and the decision owner are unresolved in the process model.
- Data required: Optical QC result; Cosmetic inspection findings; Lot identity and history; Rework and scrap criteria; Batch record contents
- Interfaces: Not specified in the source. Options: export or API from the system holding the batch record; manual or paper batch record.

**Risks** (regulatory exposure 3/5: The batch record is completed for traceability, which indicates audited records or customer-mandated controls. The process model names no specific regulation.)
- A failing lot is wrongly released to packing and reaches the customer. (severity 4/5, partial)
- A recoverable lot is scrapped when rework would have succeeded, or an unrecoverable lot is reworked, wasting cost. (severity 3/5, irreversible)
- Batch record is incomplete or incorrect, breaking traceability for the lot. (severity 3/5, partial)

**Assumptions:** The AI role analysed is recommending a disposition and drafting the batch record for human approval.; The decision owner for rework versus scrap is unknown, as the process model lists no actor.; The scrap failure mode is marked irreversible because scrapped material cannot be recovered, while the rework path recovers lots that are sent back to stage 2.

*Layer: slow. Confidence: low.*

## Cross-cutting risks

- Severe failure modes (severity 4 or more) occur at stages 4 (Recipe selection), 6 (Deposition run), 8 (Optical QC), 9 (Cosmetic inspection), 10 (Disposition and records); a human check is needed before AI output takes effect there.
- Audited records or customer-mandated controls (regulatory exposure 3 or more) apply at stages 3 (Drying and fixturing), 4 (Recipe selection), 6 (Deposition run), 8 (Optical QC), 9 (Cosmetic inspection), 10 (Disposition and records).
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
- The analysis covers where an AI agent could act. It does not assess whether a stage suits classical automation or a robotic system, so "AI role: none" does not mean there is no automation opportunity.
- Accountability for the process, the safety envelope, quality obligations and the decision to deploy stays with the process owner.
- This analysis is PROVISIONAL: the process model has not been approved by a named person, and the open questions listed in this report remain to be resolved.
- Human oversight constraint applied: mandatory.
- Provenance: Analyst scores: genuine Claude Sonnet 5.5 (medium effort) reply via the manual bridge, 21 Nov 2026, no hand edits. Process model hand-authored.

## Glossary

General definitions of the abbreviations used in this report. A plant may use some of these terms more specifically.

- **AI**: Artificial intelligence: software that performs tasks that normally need human judgment, such as recognising defects in images or recommending a setting.
- **API**: Application programming interface: a defined way for one software system to request data from, or send data to, another.
- **OPC UA**: OPC Unified Architecture: the current, vendor-neutral OPC standard (IEC 62541) for reading data from industrial equipment through one common interface.
- **PLC**: Programmable logic controller: a rugged industrial computer that runs a machine's control sequences, such as opening shutters or holding a deposition rate.
- **QC**: Quality control: checks that a product or batch meets its specification, such as measuring or inspecting samples.

### Terms to confirm

These abbreviations appear in the report but have no standard definition on file. Confirm their meaning with the process owner:

- CSV
- PDF

---
*Generated by the Robothropic AI Deployment Readiness Mapper.*
