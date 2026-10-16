// 30mm nominal fan relocation ALTERNATIVES, ONE ONLY, no real SKU. D7 source XY body z125-135.
$fn=24; site = 1;
centers=[[95,90],[95,95],[95,100]];
module review_fan(i){cx=centers[i][0];cy=centers[i][1];color([.3,.55,.7,.45])translate([cx-15,cy-15,125])cube([30,30,10]);}
for(i=[0:2]) if(site==i)review_fan(i);
// No 3D original D7 assembly included. Wood opening, airflow, thermal and current unqualified.
