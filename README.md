# yolo11n-v5n-proctoring-eval

Code and evaluation framework for a quantitative robustness audit comparing fine-tuned YOLO11n and YOLOv5n under extreme environmental degradation in automated online proctoring.

## Overview

This repository contains the training, validation, and evaluation scripts for benchmarking lightweight object detection models (YOLO11n and YOLOv5n) designed for academic integrity monitoring. 

The primary objective of this codebase is to systematically stress-test both architectures to define their **Operational Failure Point (OFP)**. By simulating challenging real-world edge cases commonly found in unsupervised webcam feeds, this framework evaluates how well the models maintain detection reliability and localization precision.

## Key Features

* **Comparative Benchmarking:** Head-to-head evaluation of YOLOv5n (baseline) and YOLO11n architectures.
* **Deterministic Stress Testing:** Implements the "Triple Threat" degradation matrix, applying sequential visual corruption to test sets.
* **Granular Metrics Tracking:** Evaluates primary accuracy (`mAP@0.5`) against strict spatial localization (`mAP@0.5-0.95`).
* **Edge-Deployment Focus:** Optimized for "Nano" class models suitable for low-latency browser or client-side inference.

## The "Triple Threat" Evaluation Matrix

The evaluation scripts in this repository test the models against isolated and compounded environmental stressors:
1. **Gaussian Blur:** Simulating motion blur and poor hardware focus.
2. **Illumination Variance:** Testing extreme underexposure and overexposure.
3. **Synthetic Occlusion:** Mimicking physical obstruction (30%–60% coverage) of prohibited items (Mobile Phones, Books, Calculators).

## Associated Dataset

The models evaluated in this repository were fine-tuned using the `Proctoring-Robustness-Audit-Dataset`, a hybrid collection of primary 720p webcam captures and open-source data subjected to combinatorial exponential augmentation (totaling 45,000 training images).

## Citation

If you utilize this code or evaluation framework, please cite the associated thesis:

```text
Isiderio, C. A., & Abonales, B. S. (2026). A Quantitative Robustness Audit of Fine-Tuned YOLOv5n and YOLO11n: Defining the Operational Failure Point in Online Automated Proctoring. Caraga State University.
