`timescale 1ns/1ps
module input_buffer_tb;
    localparam CLOCK_PERIOD = 20; // 50 MHz
    localparam DATA_WIDTH = 24;
    localparam IMG_HEIGHT = 960;
    localparam IMG_WIDTH = 1280;
    localparam input_file = "test sample files/frame.hex";

    logic clk; 
    logic resetn; 
    logic [10:0] height; 
    logic [10:0] width; 
    logic start;
    logic sof; 
    logic eol; 
    logic eof;
    logic streaming;
    logic [DATA_WIDTH-1:0] pixel_data;
    input_frame_buffer#( 
    .DATA_WIDTH (DATA_WIDTH),
    .IMG_HEIGHT (IMG_HEIGHT),
    .IMG_WIDTH (IMG_WIDTH),
    .input_file  ("test sample files/frame.hex")
    ) dut (
        clk,
        resetn,
        height,
        width,
        start,
        sof,
        eol,
        eof,
        streaming,
        pixel_data
    );
    initial clk = 0;
    always #(CLOCK_PERIOD / 2) clk = ~clk;
    initial begin
        resetn = 1;
        start = 0;
        @(posedge clk);
        resetn = 0;
        @(posedge clk);
        resetn = 1;
        @(posedge clk);
        start = 1;
        @(posedge clk);
        start = 0;
    end

    logic [DATA_WIDTH-1:0] captured [0:IMG_WIDTH*IMG_HEIGHT-1];
    logic [DATA_WIDTH-1:0] golden   [0:IMG_WIDTH*IMG_HEIGHT-1];
    int capture_idx;
    initial $readmemh("test sample files/expected_stream.hex", golden);
always_ff @(posedge clk or negedge resetn) begin
    if (!resetn) 
    begin
        capture_idx <= 0;
    end 
    else if (streaming) 
    begin
        captured[capture_idx] <= pixel_data;
        capture_idx           <= capture_idx + 1;
    end
end
    int mismatches;

    logic eof_1delay;
   always_ff @(posedge clk) begin
        if (!eof && !eof_1delay)
            eof_1delay <= 1'b0;
        if (eof)
            eof_1delay <= 1'b1;
        if (eof_1delay) begin
            mismatches = 0;
            for (int i = 0; i < IMG_WIDTH*IMG_HEIGHT; i++) begin
                if (captured[i] !== golden[i]) begin
                    mismatches++;
                    $display("MISMATCH at pixel %0d: got %h, expected %h", i, captured[i], golden[i]);
                end
            end
            if (mismatches == 0)
                $display("PASS: all %0d pixels matched", IMG_WIDTH*IMG_HEIGHT);
            else
                $display("FAIL: %0d / %0d pixels mismatched", mismatches, IMG_WIDTH*IMG_HEIGHT);
 
            $writememh("captured_output.hex", captured);  // dump for manual inspection if needed
            eof_1delay = 1'b0;
        end
    end
endmodule