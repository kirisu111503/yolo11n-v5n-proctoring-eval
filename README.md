<div align="center">
  <a href="https://git.io/typing-svg">
    <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=30&pause=1500&color=007EC6&center=true&vCenter=true&width=800&height=80&lines=yolo11n-v5n-proctoring-eval;Quantitative+Robustness+Audit;YOLO11n+vs+YOLOv5n+Performance;Automated+Online+Proctoring" alt="Typing SVG" />
  </a>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-2.9.0-ee4c2c?logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/Ultralytics-YOLO-00ffff?logo=yolo&logoColor=black" alt="YOLO">
  <img src="https://img.shields.io/badge/Google_Colab-F9AB00?logo=googlecolab&logoColor=white" alt="Colab">
</div>

---

## Overview

This repository contains the training, validation, and evaluation scripts for benchmarking lightweight object detection models (YOLO11n and YOLOv5n) designed for academic integrity monitoring. 

[cite_start]The primary objective of this codebase is to systematically stress-test both architectures to define their **Operational Failure Point (OFP)**[cite: 511]. [cite_start]By simulating challenging real-world edge cases commonly found in unsupervised webcam feeds, this framework evaluates how well the models maintain detection reliability and localization precision[cite: 512, 513].

## Key Features

* [cite_start]**Comparative Benchmarking:** Head-to-head evaluation of YOLOv5n (baseline) and YOLO11n architectures[cite: 343].
* [cite_start]**Deterministic Stress Testing:** Implements the "Triple Threat" degradation matrix, applying sequential visual corruption to test sets[cite: 350, 492].
* [cite_start]**Granular Metrics Tracking:** Evaluates primary accuracy (`mAP@0.5`) against strict spatial localization (`mAP@0.5-0.95`)[cite: 371].
* [cite_start]**Edge-Deployment Focus:** Optimized for "Nano" class models suitable for low-latency browser or client-side inference[cite: 453].

## The "Triple Threat" Evaluation Matrix

The evaluation scripts in this repository test the models against isolated and compounded environmental stressors:
1. [cite_start]**Gaussian Blur:** Simulating motion blur and poor hardware focus[cite: 345].
2. [cite_start]**Illumination Variance:** Testing extreme underexposure and overexposure[cite: 346, 476, 478].
3. [cite_start]**Synthetic Occlusion:** Mimicking physical obstruction (30%–60% coverage) of prohibited items (Mobile Phones, Books, Calculators)[cite: 347, 482].

## Usage Guide (Google Colab)

[cite_start]This project is optimized for execution in Google Colab to leverage cloud-based GPU acceleration[cite: 1321].

### 1. Training the Models
To reproduce the fine-tuning process on the custom proctoring dataset:
* Download the `yolo11n.ipynb` and `yolov5n.ipynb` notebooks from this repository.
* Upload them to Google Colab.
* [cite_start]Run the cells sequentially to initialize the dataset, apply augmentations, and execute the 200-epoch training pipeline[cite: 460].

### 2. Testing and Evaluation
To execute the quantitative robustness audit:
* Download the `test_yolo11n.ipynb` and `test_yolov5n.ipynb` notebooks.
* Upload them to Google Colab.
* Run the notebooks to automatically test the pre-trained models against the environmental stress scenarios. The scripts will systematically compute the performance degradation and output the final reliability metrics.

## Associated Dataset

[cite_start]The models evaluated in this repository were fine-tuned using the `Proctoring-Robustness-Audit-Dataset`, a hybrid collection of primary 720p webcam captures and open-source data subjected to combinatorial exponential augmentation (totaling 45,000 training images)[cite: 429, 434].

## Citation

If you utilize this code or evaluation framework, please cite the associated thesis:

```text
Isiderio, C. A., & Abonales, B. S. (2026). A Quantitative Robustness Audit of Fine-Tuned YOLOv5n and YOLO11n: Defining the Operational Failure Point in Online Automated Proctoring. Caraga State University.