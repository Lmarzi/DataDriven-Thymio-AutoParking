# Data-Driven Automatic Parking for a Thymio II Robot

> Bachelor Thesis Project - Department of Engineering and Architecture, University of Trieste (UniTS)
> 
> **Author:** Lorenzo Marzi 
> **Supervisors:** Prof. Gianfranco Fenu, Prof. Erica Salvato, Prof. Felice Andrea Pellegrino 

---

## 1. Project Objective

This project implements and experimentally validates a **data-driven control strategy** for the automatic parallel parking of a Thymio II mobile robot.

The controller is synthesized **without** an explicit, first-principles mathematical model of the robot. Instead, it "learns" the system dynamics directly from a set of experimental data. The core methodology is based on the data-driven periodic control framework developed by Pellegrino et al. (2023).

---

## 2. Methodology

The project was structured in three main phases:

### Phase 1: Data Set Generation
To synthesize the controller, a nominal "expert" trajectory was required.
* A **line-following controller** was first implemented to guide the Thymio II along a predefined, optimal parking path drawn on the ground.
* During this maneuver, **odometry** (based on wheel encoder readings) was used to record the robot's state `(x, y, θ)` and the corresponding nominal motor inputs `(v_left, v_right)`.
* Additional "perturbed" trajectories were also collected by adding disturbances to the system.

### Phase 2: Controller Synthesis
* Using the collected data (nominal and perturbed trajectories), the data-driven controller is synthesized offline.
* The scripts and data for this calculation are in the `calcolo_controllore/` folder.
* The result is a state-feedback gain matrix `K` that, when applied to the robot's state error, generates the correct motor commands to steer it back to the nominal parking trajectory.

### Phase 3: Experimental Validation
* A **Python-based GUI** (using `tkinter`) was developed to manage the PC-robot communication, run experiments, and visualize the robot's pose in real-time.
* The final controller (`Controllore/implementazione_data_driven.py`) runs on the host PC.
* It uses real-time odometry data (`odometria_real_time.py`) to estimate the robot's current state and applies the calculated control action to guide it into the parking spot.

---

## 3. Technology Stack

* **Hardware:** Thymio II Robot
* **Software & Libraries:**
    * **Python 3**
    * **tdmclient:** For asynchronous, real-time communication with the Thymio robot.
    * **tkinter:** For the graphical user interface (GUI).
    * **Numpy & SciPy:** For all numerical computation, data processing, and controller synthesis.

---

## 4. Repository Structure

* `Tesi_Lorenzo_Marzi.pdf`: The complete and final Bachelor Thesis PDF (in Italian).
* `Controllore/`: Contains the final data-driven controller implementation and the main GUI (`Thymio_GUI_driven.py`).
* `calcolo_controllore/`: Contains the raw `.csv` data and scripts used for the offline controller synthesis.
* `Dati_thymio/`: Raw `.npy` data files collected from experimental measurements (motor speeds, sensor readings, etc.).
* `Programma_per_misurare/`: Utility scripts for odometry, data acquisition, and testing.
* `Esempi_base/`: Basic examples of `tdmclient` communication.
* `Transitorio/`: Scripts and data related to motor transient response analysis.
* `usb_forte/`, `usb_lieve/`, `wifi_forte/`, `wifi_lieve/`: Folders containing data from validation experiments under different conditions (connection type and initial perturbation level).

---

## 5. How to Run

1.  **Controller Synthesis:** The scripts in `calcolo_controllore/` can be run to see how the controller gains were calculated from the `.csv` data.
2.  **Main Application:** The primary file to run the final experiment is:
    ```bash
    python Controllore/Thymio_GUI_driven.py 
    ```
    This script launches the GUI, which connects to the Thymio robot (via USB dongle) and executes the automatic parking maneuver.
