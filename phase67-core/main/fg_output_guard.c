#include "fg_output_guard.h"
static void trip(fg_control *c,const fg_output_io *io,const char *cause){
 io->write_arm(io->context,false);
 fg_fail(c,cause);
 /* Best-effort zeroing; external independent watchdog must still remove power. */
 uint8_t off[4];fg_ports(c,off);(void)io->verified_apply(io->context,off);
}
bool fg_output_commit(fg_control *c,const fg_output_io *io){
 if(!c||!io||!io->fault_healthy||!io->verified_apply||!io->write_arm)return false;
 if(!io->fault_healthy(io->context)){trip(c,io,"physical_fault");return false;}
 if(!c->arm)io->write_arm(io->context,false);
 uint8_t desired[4];fg_ports(c,desired);
 if(!io->verified_apply(io->context,desired)){trip(c,io,"bus_readback");return false;}
 if(!io->fault_healthy(io->context)){trip(c,io,"physical_fault");return false;}
 /* ARM rising edge occurs only AFTER verified_apply and fresh FAULT health. */
 if(c->arm)io->write_arm(io->context,true);
 else io->write_arm(io->context,false);
 return true;
}
