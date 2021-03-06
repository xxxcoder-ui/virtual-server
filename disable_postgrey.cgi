#!/usr/bin/perl
# Disable postgrey

require './virtual-server-lib.pl';
&can_edit_templates() || &error($text{'postgrey_ecannot'});
$err = &check_postgrey();
&error($err) if ($err);
&ui_print_header(undef, $text{'postgrey_title3'}, "");

&obtain_lock_postgrey();
&disable_postgrey();
&release_lock_postgrey();
&run_post_actions();
&webmin_log("disable", "postgrey");

&ui_print_footer("postgrey.cgi", $text{'postgrey_return'});

