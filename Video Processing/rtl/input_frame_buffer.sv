module input_frame_buffer // Using single frame testbench, can later be changed for continuos stream
#(parameter DATA_WIDTH = 24,
parameter IMG_HEIGHT = 1080,
parameter IMG_WIDTH = 1920,
parameter input_file = "test sample files/frame.hex"
)
(input wire CLOCK_50, 
input wire resetn, 
input wire [10:0] height, 
input wire [10:0] width, 
input wire start,
output logic sof, 
output logic eol, 
output logic eof,
output logic streaming,
output logic [DATA_WIDTH-1:0] pixel_data
);
localparam Y_SIZE  = IMG_WIDTH * IMG_HEIGHT;
localparam C_SIZE  = (IMG_WIDTH/2) * (IMG_HEIGHT/2);   // Cb and Cr are the same size
localparam CB_BASE = Y_SIZE;
localparam CR_BASE = Y_SIZE + C_SIZE;
localparam XW = $clog2(IMG_WIDTH);
localparam YW = $clog2(IMG_HEIGHT);
logic [7:0] mem [0:Y_SIZE + 2*C_SIZE - 1];
initial $readmemh(input_file, mem); // for sim only, replace later
logic [XW-1:0] x_cnt;
logic [YW-1:0] y_cnt;
assign eol = (x_cnt >= IMG_WIDTH - 1 && streaming) ? (1'b1) : (1'b0);
assign eof = (y_cnt >= IMG_HEIGHT - 1 && streaming && eol) ? (1'b1) : (1'b0);
assign pixel_data = { mem[y_cnt*IMG_WIDTH + x_cnt],
                       mem[CB_BASE + (y_cnt>>1)*(IMG_WIDTH/2) + (x_cnt>>1)],
                       mem[CR_BASE + (y_cnt>>1)*(IMG_WIDTH/2) + (x_cnt>>1)] };
always @ (posedge CLOCK_50 or negedge resetn)
begin
    if (!resetn)
    begin
        x_cnt <= 1'b0;
        y_cnt <= 1'b0;
        streaming<= 1'b0;
    end
    else if (start && ~streaming)
    begin
        sof <= 1'b1;
        streaming <= 1'b1;
        x_cnt <= 1'b0;
        y_cnt <= 1'b0; 
    end
    else if (streaming)
    begin
        sof <= 1'b0;
        x_cnt <= (eol) ? (1'b0) : (x_cnt + 1'b1);
        y_cnt <= (eof) ? (1'b0) : (eol) ? (y_cnt + 1'b1) : (y_cnt); 
        if (eof)
            streaming <= 1'b0;
    end
end

endmodule