# Video Processing Accelerator

**Status:** 🚧 Work in Progress (WIP)

A hardware-accelerated, multi-stage video processing pipeline designed for the DE1-SoC FPGA. This project implements a high-throughput image processing data path in SystemVerilog, featuring color space conversion, parameterized line buffering, and image upscaling.

The pipeline is verified using a hybrid simulation approach: Python scripts generate stimulus vectors from standard test images, which are fed into ModelSim testbenches, and the resulting output is compared against expected software models.

## Architecture Overview

The accelerator is structured as a streaming pipeline to process video frames in real-time. Core components include:

* **Top-Level Control:** The `top` module routes the 50MHz base clock (`CLOCK_50`) and maps the active-low hardware reset (`resetn`) to `KEY[0]`. It also manages a `new_frame_loaded` status flag for buffer synchronization.


* **Format Setup:** The `format_setup` module acts as the entry point for pre-processing data. Currently, this stage is built to unpack and align **YUV 4:2:0** video inputs. The module boundary is designed to be extensible, laying the groundwork to eventually support multiple pixel streams (such as RGB and YUV 4:2:2) across different parameterized resolutions.


* **Color Space Conversion:** Translates incoming pixel formats using fixed-point arithmetic to maintain synthesis efficiency without floating-point overhead.
* **Line Buffers:** Uses block RAM (BRAM) to store sequential image rows, providing the localized spatial data required for 2D filtering and scaling operations.
* **Upscaling Engine:** Interpolates pixel data to scale images to target resolutions, driven by parameterized dimensions.

## Technology Stack

* **Hardware Description:** SystemVerilog, RTL
* **Simulation & Verification:** ModelSim
* **Test Scripting:** Python (NumPy, Pillow/OpenCV for image-to-vector generation)
* **Synthesis & Implementation:** Intel Quartus Prime
* **Target Hardware:** DE1-SoC (Cyclone V)

## Verification Flow

To ensure hardware behavior matches the mathematical model, the verification flow operates in three steps:

1. **Stimulus Generation:** A Python script reads a test image, converts it to the currently supported YUV 4:2:0 format, and dumps the raw hex pixel values into a `.mem` or `.txt` file.
2. **RTL Simulation:** The ModelSim testbench reads the stimulus file, drives the SystemVerilog pipeline, and captures the processed output vectors.
3. **Output Analysis:** A second Python script reconstructs the output vectors back into an image format and calculates the error delta against a pure software implementation to verify fixed-point accuracy.

## Current Progress

This project is currently in active development. Recent milestones include:

* Establishing the top-level integration shell and board-level I/O mappings.


* Defining the module boundaries for the format setup stage and establishing baseline YUV 4:2:0 ingestion.


* Drafting the RTL for the color space conversion and testing fixed-point coefficient accuracy.
* Building the Python tooling for image-to-hex stimulus generation.

## Next Steps / Roadmap

* **Multi-Format & Resolution Expansion:** Expand the `format_setup` logic beyond the current YUV 4:2:0 baseline to seamlessly ingest, decode, and align RGB and YUV 4:2:2 pixel streams at varying parameterized resolutions.
* **Line Buffer Integration:** Complete the memory controller logic to seamlessly feed the line buffers into the upscaler without dropping pixels.
* **Pipeline Synchronization:** Implement valid/ready handshake signals across all modules to handle backpressure and pipeline stalling.
* **Full Data Path Simulation:** Run the complete Python-to-ModelSim loop on a full 1080p equivalent frame to verify latency and throughput.
* **Quartus Synthesis:** Map the design onto the DE1-SoC, run timing analysis to ensure it meets the 50MHz clock constraint, and verify resource utilization (ALMs, DSP blocks, and M10K blocks).
