---
dmc: DMC-GAIAPULSE-GPAM-AMPEL-0201-06-003-A-001-00_EN-US
ident:
  dmCode: GPAM-AMPEL-0201-06-003-A
  modelIdentCode: AMPEL360
  systemDiffCode: A
  systemCode: 06  # Dimensions and Areas
  subSystemCode: 00
  subSubSystemCode: 00
  assyCode: 000
  disassyCode: 00
  disassyCodeVariant: A
  infoCode: 003  # Measurement Point Definitions
  infoCodeVariant: A
  itemLocationCode: 00
  language: EN-US
applicability: AMPEL360XWLRGA
status: draft
security: proprietary - GAIA AIR Internal Use Only
responsiblePartnerCompany: GAIAPULSE
originator: Amedeo Pelliccia & AI Collaboration
date: 2025-03-14
---

# AMPEL360XWLRGA Measurement Point Definitions

**Document ID (COAFI IN):** GPAM-AMPEL-0201-06-003-A
**Version:** 1.0
**Date:** 2025-03-14
**Author:** Amedeo Pelliccia & AI Collaboration
**Status:** Draft
**Classification:** Internal / Restricted

[Back to Part II Index](../../index.md)

## 1. Introduction

This document defines the measurement points and key dimensions for the AMPEL360XWLRGA aircraft. These measurements are used for defining the aircraft's geometry, locating components, and verifying alignment during assembly and maintenance.

## 2. Coordinate System

*   **Origin:** The origin (0, 0, 0) of the coordinate system is located at the tip of the nose cone (Point AP).
*   **X-axis:** Positive X extends towards the rear of the aircraft (aft).
*   **Y-axis:** Positive Y extends towards the starboard (right) side of the aircraft.
*   **Z-axis:** Positive Z extends *downwards* from the aircraft.
*   **Units:** All coordinates are provided in both meters (m) and feet (ft).
* **Datum:** All measurements in this document are relative to the aircraft datum, located at the tip of the nose cone (point AP).

## 3. Aircraft Configurations

The following table defines the aircraft configurations referenced in the measurement point table:

| Configuration           | MRW (kg) | Fwd CG Limit (% MAC) | Aft CG Limit (% MAC) | Notes                                   |
| :---------------------- | :------- | :------------------- | :------------------- | :-------------------------------------- |
| Baseline                | [COMPLETAR]    | [COMPLETAR]            | [COMPLETAR]             | Empty aircraft, standard configuration. |
| MRW - Forward CG        | 268,900  | 26                   | 33.1                | Maximum Ramp Weight, forward CG limit.  |
| MRW - Aft CG            | 268,900  | 26                   | 33.1                | Maximum Ramp Weight, aft CG limit.     |
| Lighter Configuration   | 135,000  | 20                   | 40                   | Specific operational weight.            |
| A/C Jacked            |  -  |      -              |        -               | Aircraft Jacked configuration           |

**Note:** %MAC refers to the percentage of the Mean Aerodynamic Chord.  The MAC is defined in document [Placeholder: Link to document defining MAC].

## 4. Measurement Points

| Reference Point | Baseline (m) | Baseline (ft) | MRW Fwd CG (m) | MRW Fwd CG (ft) | MRW Aft CG (m) | MRW Aft CG (ft) | Lighter Config (m) | Lighter Config (ft) | A/C Jacked (m) |  A/C Jacked (ft) |
| :-------------- | :----------- | :------------ | :------------- | :--------------- | :------------- | :--------------- | :----------------- | :------------------ | :------------: | :----------------: |
| AP              | 6.61         | 21.69         | 6.55           | 21.49            | 6.83           | 22.41            | 6.52             | 21.39              |        7.72       |      25.33         |
| BF1             | 2.44         | 8.01          | 2.46           | 8.07             | 2.56           | 8.40             | 2.66             | 8.73               |       3.71        |       12.17         |
| BF2             | 1.93         | 6.33          | 1.93           | 6.33             | 2.07           | 6.79             | 2.08             | 6.82               |       3.16        |       10.37         |
| BF3             | 3.09         | 10.14       | 2.50           | 8.20             | 2.68           | 8.79             | 2.59             | 8.50               |        3.71       |       12.17         |
| C1              | 2.52         | 8.27         | 3.13           | 10.27            | 3.19           | 10.47            | 3.37             | 11.06              |        4.39       |       14.40          |
| C2              | 3.25         | 10.66         | 3.22           | 10.56            | 3.43           | 11.25            | 3.29             | 10.79              |        4.43       |       14.53         |
| C3              | 3.25         | 10.66         | 3.21           | 10.53            | 3.43           | 11.25            | 3.26             | 10.70              |        4.41       |        14.47        |
| CP1             | 5.84         | 19.16         | 5.90           | 19.36            | 5.93           | 19.46            | 6.20             | 20.34              |       7.18        |       23.56         |
| D1              | 5.05         | 16.57         | 5.10           | 16.73            | 5.15           | 16.90            | 5.37             | 17.62              |        6.37       |        20.90        |
| D2              | 5.10         | 16.73         | 5.12           | 16.80            | 5.22           | 17.13            | 5.33             | 17.49              |        6.37       |       20.90         |
| D3              | 5.17         | 16.92         | 5.15           | 16.90            | 5.32           | 17.45            | 5.27             | 17.29              |        6.37       |       20.90         |
| D4              | 5.22         | 17.13         | 5.18           | 17.00            | 5.41           | 17.75            | 5.21             | 17.09              |      6.37         |         20.90       |
| D5              | 7.25         | 23.79         | 7.31           | 23.98            | 7.33           | 24.05            | 7.61             | 24.97              |       8.59        |        28.18        |
| F1              | 2.41         | 7.91          | 2.45           | 8.04             | 2.51           | 8.23             | 2.70             | 8.86               |        3.71       |        12.17        |
| F2              | 2.53         | 8.30          | 2.50           | 8.20             | 2.70           | 8.86             | 2.58             | 8.46               |       3.71        |       12.17         |
| F3              | 8.50         | 27.89         | 8.54           | 28.02            | 8.61           | 28.25            | 8.78             | 28.81              |        9.80       |        32.15        |
| F4              | 8.41         | 27.59         | 8.38           | 27.49            | 8.59           | 28.18            | 8.45             | 27.72              |        9.58       |         31.43       |
| FT1             | 3.72         | 12.21         | 3.71           | 12.17            | 3.87           | 12.70            | 3.84             | 12.60              |         4.94      |        16.21        |
| FT2             | 4.53         | 14.86         | 4.52           | 14.83            | 4.68           | 15.35            | 4.64             | 15.22              |       5.74        |         18.83       |
| FT3             | 5.17         | 16.96         | 5.16           | 16.93            | 5.32           | 17.45            | 5.27             | 17.29              |        6.38       |        20.93        |
| HT              | 7.67         | 25.16         | 7.60           | 24.93            | 7.88           | 25.85            | 7.56             | 24.80              |      8.77         |      28.77         |
| N1              | 0.74         | 2.43          | 0.75           | 2.46             | 0.87           | 2.85             | 0.93             | 3.05               | 1.99              | 6.53               |
| RD1             | 3.98         | 13.06         | 4.04           | 13.26            | 4.06           | 13.32            | 4.34             | 14.24              |  -                |     -              |
| VT              | 17.17        | 56.33         | 17.10          | 56.10            | 17.39          | 57.05            | 17.07            | 56.00              |         18.27      |        59.94        |
| WL1             | -            | -            | -            | -            | -           | -            | -             | -              |       10.57         |          34.68       |
| WL2             | 6.98         | 22.90         | 6.96           | 22.84            | 7.14           | 23.43            | 7.04             | 23.10              |         8.17       |        26.80        |

**Notes:**

1.  **Water Lines (WL1, WL2):** Water Lines are horizontal reference planes. X coordinates are not applicable.
2. **FDL:** The Fuselage Datum Line is not a discrete measurement point, but a line used for referencing the overall geometry.

## 5. Reference Point Definitions

[Placeholder:  Provide a detailed definition of each reference point (AP, BF1, BF2, etc.).  Include a diagram if possible. Example:]

*   **AP (Aft Perpendicular):** A vertical reference plane located at the tip of the aircraft's nose cone.  This serves as the origin (0, 0, 0) for the aircraft coordinate system.
*   **BF1, BF2, BF3 (Belly Fairing):**  Points located on the belly fairing. [Provide precise definitions relative to fuselage stations and waterlines.]
* **HT:** Horizontal Tail.
* **RD1:** Rudder point.
*   **C1, C2, C3:** [Provide precise definitions, likely related to wing stations.]
*   **CP1:** Cockpit Point. [Provide precise definition, likely related to pilot eye position.]
*   **D1, D2, D3, D4, D5:** [Provide precise definitions, likely related to fuselage stations and landing gear attachment points.]
*   **F1, F2, F3, F4:** [Provide precise definitions, likely related to fuselage stations.]
*   **FT1, FT2, FT3:** [Provide precise definitions, likely related to tail stations
