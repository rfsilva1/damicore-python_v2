
ppmd.exe - PPMd_sh executable built with IntelC (for win32)

ppmd.cpp - CLI and main processing loop (also this is the source file to compile)
file_process.inc - main processing loop
timer.inc - GetTickCount-based timer functions
def_date.inc - date constant rearrangement
sh_v1m.inc - Dummy rangecoder with carries (simple, precise, and slow)
sh_v1x.inc - Faster and somewhat imprecise rangecoder
E89_v2a.inc - E8 filter class
model.inc - "Model" class
ppmd_byte.inc - Model::ProcessByte() function (byte encode/decode)
ppmd_proc0.inc - Encode/decode symbol (or escape) in determinisic "binary" context
ppmd_proc1.inc - Encode/decode symbol in "unmasked" context (highest order)
ppmd_proc2.inc - Encode/decode symbol in "masked" context (after at least one escape)
ppmd_update.inc - context update function
ppmd_init.inc - model init function
ppmd_flush.inc - model flush function (calls tree init or cutoff)
mod_cutoff.inc - a function for tree shrinking on memory overflow
mod_context.inc - "STATE" and "PPM_CONTEXT" classes
mod_rescale.inc - a function to rescale the statistics in a context (to avoid byte overflow)
mod_see.inc - "SEE2_CONTEXT" class (SEE in masked contexts)
alloc_node.inc - "BLK_NODE" class
alloc_units.inc - custom memory allocation functions (for statistical tree nodes)
