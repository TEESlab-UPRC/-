![AIM-01_cropped](https://github.com/user-attachments/assets/4b4474d7-7416-4064-9a08-6f17f363098e)

## Contents
- [Contents](#contents)
- [About](#about)
- [Quick start](#quick-start)
- [Documentation](#documentation)
- [Citing ΑΙΜ](#citing-bsam)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## About
The Adaptive polIcymaking Model (AIM) is a decision support model which enables the exploratory analysis of policy/strategy pathways towards the achievement of one or multiple targets, identifying in parallel their conditions of success. To do so, AIM performs meta-analysis of simulations models’ outputs, and evaluates the performance of selected policies/strategies over many combinations of a large number of contextual uncontrollable variables (scenarios). Then, it visualizes successful policy pathways towards a predefined target, and sets up a monitoring system for real-world policy adaptations in case of unexpected contextual future evolutions.

The novelty of AIM lies in (i) using a simple clustering logic, thus it can be easily adapted for soft-linking with a wide variety of models, (ii) generating adaptive policies for different contexts, by changing the limits of the uncontrollable variables (scenarios), making it a useful tool for application at various scales and contexts, and (iii) facilitating interactive stakeholder consultation for the design of policy pathways, through real-time and easily interpretable visualizations. ΑΙΜ is written in Python. It is maintained by the [Techno-Economics of Energy Systems laboratory (TEESlab)](https://teeslab.unipi.gr) at the University of Piraeus and is freely available on GitHub. 

## Quick start
* Install Python 3.9
* Download ΑΙΜ from Github and save it in a folder of your preference
* Using a terminal (command line) navigate to the folder where ΑΙΜ is saved 
* Type pip install -r requirements.txt
* Type python main.py to run the preconfigured example

## Documentation
The documentation of AIM will soon be available.

## Citing AIM
In academic literature please cite AIM as: 
>[![article DOI](https://img.shields.io/badge/article-10.1016/j.egyr.2021.07.052-blue)](https://doi.org/10.1016/j.enpol.2020.111350) Michas, S., Stavrakas, V., Papadelis, S., & Flamos, A. (2020). A transdisciplinary modeling framework for the participatory design of dynamic adaptive policy pathways. *Energy Policy*, *139*, 111350. [https://doi.org/10.1016/j.enpol.2020.111350](https://doi.org/10.1016/j.enpol.2020.111350)


## License
The **AIM source code**, consisting of the *.py* files, is licensed under the GNU Affero General Public License:

    Copyright (C) 2024 Technoeconomics of Energy Systems laboratory - University of Piraeus Research Center (TEESlab-UPRC)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Acknowledgements
The development of AIM has been partially funded by the following sources:
* The project funded by the Swiss Federal Office for Energy (SFOE), titled “Swiss Policy towards Zero CO2 Emissions compatible with European Decarbonization Pathways” (POLIZERO) – Contract No. SI/502149-01 
* The EC funded Horizon 2020 Framework Programme for Research and Innovation (EU H2020) Project titled "Sustainable energy transitions laboratory" (SENTINEL) with grant agreement No. 837089
* The EC funded Horizon 2020 Framework Programme for Research and Innovation (EU H2020) Project titled "Transition pathways and risk analysis for climate change policies" (TRANSrisk) with grant agreement No. 642260
