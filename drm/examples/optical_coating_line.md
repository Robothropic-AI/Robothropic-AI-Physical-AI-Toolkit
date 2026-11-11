# Worked example: anti-reflective coating of optical lenses (batch vacuum deposition)

> **Illustrative process.** Drafted from general engineering knowledge, not taken from a real plant.
> It describes the line **as it runs today, with human operators**. The DRM's job is to analyse where
> AI could be inserted; the process as written contains no AI.

**Process: Anti-reflective coating of optical lenses, batch vacuum deposition line**

1. Incoming inspection: the operator visually inspects each lot of lens substrates for scratches, chips and contamination, and logs the lot number and findings.
2. Ultrasonic cleaning: the operator loads substrates into baskets, selects the cleaning recipe for the lot, and runs them through a multi-tank ultrasonic line.
3. Drying and fixturing: after drying, the operator mounts substrates in the coating fixture (planetary dome) in a laminar-flow area, recording positions.
4. Chamber loading and pump-down: the operator loads the dome into the vacuum chamber and starts pump-down. The process waits until base pressure is reached.
5. Recipe selection: the process engineer selects the coating recipe (layer materials, thicknesses, deposition rates) from the recipe library and confirms it against the customer specification.
6. Deposition run: e-beam evaporation with ion assist runs the layer sequence. The PLC controls shutters and rates, thickness is monitored by quartz crystal and optical monitoring, and the operator watches for deviations and can abort the run.
7. Venting and unloading: the chamber is vented, the dome cools, and the operator unloads the substrates.
8. Optical QC: witness samples are measured on a spectrophotometer, and reflectance is compared against the specification to give pass or fail.
9. Cosmetic inspection: the operator inspects each lens under an inspection lamp for pinholes, haze and stains.
10. Disposition and records: passing lots are released to packing. Failing lots go to rework (strip and recoat, returning to stage 2) or scrap. The batch record is completed for traceability.
