#!/usr/bin/perl
# Collect various pieces of general system information, for display by themes
# on their status pages. Run every 5 mins from Cron.

package virtual_server;
$main::no_acl_check++;
require './virtual-server-lib.pl';
$start = time();

# Make sure we are not already running
if (&test_lock($collected_info_file)) {
	print "Already running\n";
	exit(0);
	}

# Don't diff collected file
$gconfig{'logfiles'} = 0;
$gconfig{'logfullfiles'} = 0;
$WebminCore::gconfig{'logfiles'} = 0;
$WebminCore::gconfig{'logfullfiles'} = 0;
$no_log_file_changes = 1;
&lock_file($collected_info_file);

$info = &collect_system_info();
if ($info) {
	if ($config{'collect_restart'}) {
		&restart_collected_services($info);
		}
	&save_collected_info($info);
	&add_historic_collected_info($info, $start);
	}
&unlock_file($collected_info_file);

# Update IP list cache
&build_local_ip_list();

# Update SPF and DMARC caches
&build_spf_dmarc_caches();

# Update DB of per-user last login times
&update_last_login_times();

# For any domains that are due for a let's encrypt cert renewal, do it now
&apply_letsencrypt_cert_renewals();

# Resync all jails
&copy_all_domain_jailkit_files();

# Kill disallowed server processes
if ($config{'check_ports'} == 2) {
	foreach my $d (grep { $_->{'unix'} && !$_->{'parent'} }
			    &list_domains()) {
		&kill_disallowed_domain_server_ports($d);
		}
	}

# Cleanup session files for domains with a website
if ($config{'php_session_age'}) {
	foreach my $d (grep { &domain_has_website($_) } &list_domains()) {
		my @f = &cleanup_php_sessions($d, 0);
		foreach my $f (@f) {
			}
		}
	}

&run_post_actions_silently();
