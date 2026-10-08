module top (input wire CLOCK_50,
wire resetn,
wire new_frame_loaded; // 1 for loaded in buffer, 0 for loading/not loaded
);
assign resetn = KEY[0]; // Reset when 0
assign new_frame_loaded = 0;

endmodule
