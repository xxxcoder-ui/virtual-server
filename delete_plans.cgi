#!/usr/bin/perl
# Delete one or more selected plans

require './virtual-server-lib.pl';
&ReadParse();
&error_setup($text{'dplans_err'});
$canplans = &can_edit_plans();
$canplans || &error($text{'plans_ecannot'});

# Get the plans and remove them
@d = split(/\0/, $in{'d'});
@d || &error($text{'dplans_enone'});
@plans = &list_editable_plans();
@allplans = &list_plans();
foreach $d (@d) {
	($plan) = grep { $_->{'id'} eq $d } @plans;
	if ($plan) {
		@allplans = grep { $_->{'id'} ne $d } @allplans;
		@allplans || &error($text{'dplans_eall'});
		&delete_plan($plan);
		}
	}

# Log and return
&run_post_actions_silently();
&webmin_log("delete", "plans", scalar(@d));
&redirect("edit_newplan.cgi");

