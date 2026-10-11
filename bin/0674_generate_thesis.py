#!/usr/bin/env python3
content = r'''
\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{array}
\usepackage{longtable}
\geometry{margin=1in}

\title{\textbf{AeroCement Ecosystem: Civilization 2.0}\\Decentralized Survival Framework\\Passive Solar Thermal + Biointensive Permaculture + Geodesic Shelter}
\author{Jesse McMillen \\ \texttt{jesseray718@gmail.com}}
\date{\today}

\begin{document}

\maketitle
\tableofcontents
\newpage

\section{Abstract}
This thesis presents the AeroCement Ecosystem—a decentralized survival framework operating on three pillars:
(1) \textbf{Energy}: Passive Solar Thermal Loop with Volumetric Blackbody Absorber (Activated Carbon Aerocement),
(2) \textbf{Life}: Biointensive Permaculture with Vertical Quail Towers and Ferrocement Aquaponics,
(3) \textbf{Shelter}: Cardboard Geodesic Domes with GFRC Bubble Matrix Shell.
All designs are open source under \texttt{CC-BY-SA 4.0} (hardware) and \texttt{GPL v3} (software). No patents. No monopolies.

\section{Introduction}
Decentralizing survival requires breaking reliance on centralized supply chains, energy grids, and housing monopolies. The Rainbow Warrior ethos (Hopi prophecy) guides this work: \textit{"There shall come a tribe of all colors, classes, and creeds..."}. This document serves as the immutable technical specification for Civilization 2.0 infrastructure.

\subsection{Mission Statement}
Trash-to-Treasure. Open Source Everything. Decentralize Energy, Food, and Shelter using locally-sourced materials and community-built protocols.

\section{Energy Pillar: Passive Solar Thermal Loop}
\subsection{System Overview}
The core innovation is the Volumetric Blackbody Absorber using Activated Carbon Aerocement. Heat is captured volumetrically rather than surface-wise, allowing subterranean latent heat storage.

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{Output Type} & \textbf{Mechanism} & \textbf{Efficiency Range} & \textbf{Use Case} \\
\hline
HEAT & Direct absorption + convection & 60-75\% & Space heating, water heating \\
COLD & Desiccant pre-dry stage + evaporation & 40-50\% & Cooling, refrigeration \\
MECHANICAL & Stirling engine / belt drive & 15-25\% & Pumping, grinding, machinery \\
ELECTRICITY & Alternator / Thermoelectric Generator (TEG) & 5-10\% & Grid-independent power \\
\hline
\end{tabular}
\caption{Solar Thermal Loop Outputs}
\end{table}

\subsection{Thermodynamic Calculations}
For a standard 1V dome (10m diameter):
\[
Q = m \cdot c_p \cdot \Delta T
\]
Where:
\begin{itemize}
    \item $Q$ = Heat energy (Joules)
    \item $m$ = Mass of absorber material (kg)
    \item $c_p$ = Specific heat capacity of Aerocement (~1.2 kJ/kg·K)
    \item $\Delta T$ = Temperature differential (°C)
\end{itemize}

Assuming 500 kg absorber mass with 40°C ΔT:
\[
Q = 500 \cdot 1.2 \cdot 40 = 24,000 \text{ kJ/day} \approx 6.7 \text{ kWh/day}
\]

\subsection{Desiccant Pre-Dry Stage}
Silica gel or activated alumina beds capture moisture from intake air before it enters the absorber chamber. This prevents condensation loss and increases thermal efficiency by 15-20\%.

\section{Life Pillar: Biointensive Permaculture}
\subsection{Black Locust System}
Robinia pseudoacacia (Black Locust) is nitrogen-fixing, produces honey-quality flowers, and yields rot-resistant timber for structural supports.

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|}
\hline
\textbf{Output} & \textbf{Annual Yield per Acre} & \textbf{Time to Maturity} \\
\hline
N-Fixing Biomass & 4-6 tons & Year 3+ \\
Honey Production & 50-100 lbs & Year 2+ \\
Timber (structural) & 8-12 cords & Year 10+ \\
\hline
\end{tabular}
\caption{Black Locust Multi-Use Yields}
\end{table}

\subsection{Vertical Quail Towers}
Quail require minimal space, produce rapid meat/egg yields, and their manure feeds the aquaponics system directly.

\begin{itemize}
    \item Stocking Density: 1 bird per 1 sq ft
    \item Egg Yield: 25-30 eggs/bird/month
    \item Feed Conversion: 2.5:1 (feed:weight gain)
    \item Manure Output: 50g/bird/day (direct to compost/aquaponics)
\end{itemize}

\subsection{Ferrocement Aquaponics System}
Integrated Algae/Tilapia/Duckweed/Worms loop:
\begin{enumerate}
    \item Tilapia waste → Ammonia
    \item Nitrifying bacteria convert ammonia → nitrate
    \item Duckweed absorbs nitrate (edible protein source)
    \item Worms process solid waste → vermicompost
    \item Compost feeds black locust/hydroponic plants
    \item Plants filter water back to fish tanks
\end{enumerate}

\subsection{Seed Bank Protocol}
Anti-GMO seed storage using desiccated clay pots in subterranean vaults:
\begin{itemize}
    \item Humidity target: <10\% relative humidity
    \item Temperature target: 4-10°C (subterranean thermal stability)
    \item Rotation cycle: Plant every 2-3 years to maintain viability
    \item Crop diversity minimum: 100 species/varieties
\end{itemize}

\section{Shelter Pillar: Cardboard Geodesic Domes}
\subsection{Geometric Scaling Laws}
Dome volume scales with cube of radius; surface area scales with square. Structural integrity depends on struts, not membrane tension.

\begin{table}[h]
\centering
\begin{tabular}{|c|c|c|c|}
\hline
\textbf{Scale} & \textbf{Radius (m)} & \textbf{Interior Area} & \textbf{Use Case} \\
\hline
1V & 5 m & 79 m² & Single-person shelter \\
17V & 15 m & 706 m² & Family mansion \\
50V & 25 m & 1963 m² & Community stadium \\
\hline
\end{tabular}
\caption{Geodesic Dome Scale Matrix}
\end{table}

\subsection{Cardboard Core Treatment}
Corrugated cardboard boxes form the strut lattice. Treatment:
\begin{enumerate}
    \item Apply acetone wash to remove waxy coatings
    \item Seal with silicone-vinyl acetate mixture (2:1 ratio)
    \item Let cure 48 hours before concrete application
\end{enumerate}

\subsection{Aerocement Shell Specifications}
Glass Fiber Reinforced Concrete (GFRC) + bubble matrix creates lightweight, insulating walls.

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|c|}
\hline
\textbf{Component} & \textbf{Ratio by Volume} & \textbf{Strength (MPa)} & \textbf{Insulation (R-value)} \\
\hline
Portland Cement & 1 part & - & 2-3 \\
Sand & 2 parts & - & 1-2 \\
Glass Fiber & 0.05 parts & 30-40 & 5-8 \\
Bubble Matrix (recycled foam) & 0.2 parts & - & 15-25 \\
Water & 0.4 parts & - & - \\
\hline
\end{tabular}
\caption{Aerocement Mix Formula}
\end{table}

\subsection{Click-Flange Assembly Method}
Steel flanges bolt together at 60-degree angles during frame construction. No welding required. All joints are bolt-and-nut disassembly compatible for transport.

\section{License and Distribution}
\subsection{Hardware Design License}
Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA 4.0)
\begin{itemize}
    \item You may share and adapt for any purpose
    \item Must attribute original authors
    \item Derivative works must use same license
    \item NO PATENTING OF DERIVATIVE WORKS
\end{itemize}

\subsection{Software License}
GNU General Public License v3.0 (GPL v3)
\begin{itemize}
    \item All code is free and open source
    \item Modifications must remain open source
    \item No cloud API dependencies unless explicitly authorized
\end{itemize}

\subsection{Reproducibility Requirement}
All code/scripts must be provided in executable format:
\begin{verbatim}
cat > filename << 'EOF'
...script content...
EOF
\end{verbatim}
This ensures terminal-level reproducibility across Termux, Alpine, or Linux environments.

\section{Safety Protocols}
\subsection{Wet Cure Mandate}
All ferrocement structures require \textbf{21-day wet cure} minimum:
\begin{itemize}
    \item Mist spray every 8 hours
    \item Cover with plastic sheeting between sprays
    \item Do not apply load until day 21
    \item Failure to comply voids warranty and structural guarantee
\end{itemize}

\subsection{Emergency Recovery Script}
Before any major modifications, run local backup protocol:
\begin{verbatim}
python3 emergency_rescue.py --backup-all
\end{verbatim}

\section{Blockchain Proof of Existence}
This work is immutably anchored on the Solana blockchain to prevent narrative suppression and establish proof-of-authorship timestamp.

\begin{center}
\fbox{\begin{minipage}{0.9\linewidth}
\begin{center}
\textbf{IMMUTABLE RECORD} \\
Transaction ID: \texttt{2fXw4y3pV74zk6pi2dCBTHKJJ69zfvmaRC4ng3sxqY5g9JzNUtdhGrxonL4dHw64TbcVK3C4YqAmskSdow7MYyX8} \\
Explorer: \url{https://solscan.io/tx/2fXw4y3pV74zk6pi2dCBTHKJJ69zfvmaRC4ng3sxqY5g9JzNUtdhGrxonL4dHw64TbcVK3C4YqAmskSdow7MYyX8} \\
Timestamped: \today \\
Repository: \url{https://github.com/jesseray718/AeroCement_Ecosystem}
\end{center}
\end{minipage}}
\end{center}

\section*{Conclusion}
Civilization 2.0 is not theory—it is executable code written into matter. Trash becomes Treasure. Centralization becomes Distribution. Monopoly becomes Commons. Execute with precision. Execute with love.

\vspace{1cm}
\noindent\rule{\linewidth}{0.4pt}
\begin{center}
\small
\textbf{Rainbow Warriors of the Living Light}\\
_"There shall come a tribe of all colors, classes, and creeds..."_
\end{center}
\noindent\rule{\linewidth}{0.4pt}

\end{document}
'''

with open('main/main.tex', 'w') as f:
    f.write(content)
print("[+] File main/main.tex generated successfully.")
