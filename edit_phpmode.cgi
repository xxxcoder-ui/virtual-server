#!/usr/bin/perl
# Show web and PHP options for a virtual server

require './virtual-server-lib.pl';
&ReadParse();
$d = &get_domain($in{'dom'});
&can_edit_domain($d) || &error($text{'edit_ecannot'});
$can = &can_edit_phpmode($d);
$can || &error($text{'phpmode_ecannot'});
if (!$d->{'alias'}) {
	@modes = &supported_php_modes($d);
	$mode = &get_domain_php_mode($d);
	}
$p = &domain_has_website($d);

&ui_print_header(&domain_in($d), $text{'phpmode_title'}, "");

print &ui_form_start("save_phpmode.cgi");
print &ui_hidden("dom", $d->{'id'}),"\n";
print &ui_hidden_table_start($text{'phpmode_header'}, "width=100%", 2,
			     "phpmode", 1, [ "width=30%" ]);

if (!$d->{'alias'} && $can == 2 &&
    ($p eq 'web' || &plugin_defined($p, "feature_get_web_php_mode"))) {
	# PHP execution mode
	print &ui_table_row(&hlink($text{'phpmode_mode'}, "phpmode"),
			    &ui_radio_table("mode", $mode,
			      [ map { [ $_, $text{'phpmode_'.$_} ] }
				    @modes ]));

	# Warn if changing mode would remove per-dir versions
	if ($mode eq "cgi" || $mode eq "fcgid") {
		@dirs = &list_domain_php_directories($d);
		if (@dirs > 1) {
			print &ui_table_row("", $text{'phpmode_dirswarn'});
			}
		}
	}

# PHP fcgi sub-processes
if (!$d->{'alias'} && &indexof("fcgid", @modes) >= 0 && $can == 2 &&
    ($p eq 'web' || &plugin_defined($p, "feature_get_web_php_children"))) {
	$children = &get_domain_php_children($d);
	if ($children > 0) {
		print &ui_table_row(&hlink($text{'phpmode_children'},
					   "phpmode_children"),
				    &ui_opt_textbox("children", $children || '',
					 5, $text{'tmpl_phpchildrennone'}));
		}
	}

# PHP max execution time, for fcgi mode
if (!$d->{'alias'} &&
    (&indexof("fcgid", @modes) >= 0 || &indexof("fpm", @modes) >= 0) &&
    ($p eq 'web' ||
     &plugin_defined($p, "feature_get_fcgid_max_execution_time"))) {
	$max = $mode eq "fcgid" ? &get_fcgid_max_execution_time($d)
				: &get_php_max_execution_time($d);
	print &ui_table_row(&hlink($text{'phpmode_maxtime'}, "phpmode_maxtime"),
			    &ui_opt_textbox("maxtime", $max, 5,
					    $text{'form_unlimit'})." ".
			    $text{'rfile_secs'});
	}

# Ruby execution mode
if (defined(&supported_ruby_modes)) {
	@rubys = &supported_ruby_modes($d);
	if (!$d->{'alias'} && @rubys && $can == 2 &&
	    ($p eq 'web' || &plugin_defined($p, "feature_get_web_ruby_mode"))) {
		print &ui_table_row(
			&hlink($text{'phpmode_rubymode'}, "rubymode"),
			&ui_radio_table("rubymode", &get_domain_ruby_mode($d),
				  [ [ "", $text{'phpmode_noruby'} ],
				    map { [ $_, $text{'phpmode_'.$_} ] }
					@rubys ]));
		}
	}

# Write logs via program. Don't show unless enabled.
if ((!$d->{'alias'} || $d->{'alias_mode'} != 1) && $can == 2 &&
    &get_writelogs_status($d) && $p eq 'web') {
	print &ui_table_row(
		&hlink($text{'newweb_writelogs'}, "template_writelogs"),
		&ui_yesno_radio("writelogs", &get_writelogs_status($d)));
	}

# Match all sub-domains
if ($p eq 'web' || &plugin_defined($p, "feature_get_web_domain_star")) {
	print &ui_table_row(&hlink($text{'phpmode_matchall'}, "matchall"),
		    &ui_yesno_radio("matchall", &get_domain_web_star($d)));
	}

# Server-side includes
if ($p eq 'web' || &plugin_defined($p, "feature_get_web_domain_ssi")) {
	($ssi, $suffix) = &get_domain_web_ssi($d);
	$suffix = ".shtml" if ($ssi != 1);
	print &ui_table_row(&hlink($text{'phpmode_ssi'}, "phpmode_ssi"),
	    &ui_radio("ssi", $ssi,
		      [ [ 1, &text('phpmode_ssi1',
				   &ui_textbox("suffix", $suffix, 6)) ],
			[ 0, $text{'no'} ],
			$ssi == 2 ? ( [ 2, $text{'phpmode_ssi2'} ] )
				  : ( ) ]));
	}

# Default website for its IP
if (!$d->{'alias'} || $d->{'alias_mode'} != 1 &&
    ($p eq 'web' || &plugin_defined($p, "feature_get_web_default_website"))) {
	$defweb = &is_default_website($d);
	$defd = &find_default_website($d);
	$defno = $defd ? &text('phpmode_defno', $defd->{'dom'}) : $text{'no'};
	if (&can_default_website($d) && !$defweb) {
		print &ui_table_row(&hlink($text{'phpmode_defweb'}, "defweb"),
			&ui_radio("defweb", $defweb,
				  [ [ 1, $text{'yes'} ], [ 0, $defno ] ]));
		}
	else {
		print &ui_table_row(&hlink($text{'phpmode_defweb'}, "defweb"),
			$defweb == 1 ? $text{'yes'} :
			$defweb == 2 ? $text{'phpmode_defwebsort'} :
				       $defno);
		}
	}

# Log file locations
if (!$d->{'alias'} && &can_log_paths() &&
    ($p eq 'web' || &plugin_defined($p, "feature_change_web_access_log"))) {
	$alog = &get_website_log($d, 0);
	if ($alog) {
		print &ui_table_row(&hlink($text{'phpmode_alog'}, 'accesslog'),
			&ui_textbox("alog", $alog, 60));
		}
	$elog = &get_website_log($d, 1);
	if ($elog) {
		print &ui_table_row(&hlink($text{'phpmode_elog'}, 'errorlog'),
			&ui_textbox("elog", $elog, 60));
		}
	}

# HTML directory
if (!$d->{'alias'} && $d->{'public_html_dir'} !~ /\.\./ && $p eq 'web') {
	print &ui_table_row(&hlink($text{'phpmode_htmldir'}, 'htmldir'),
		&ui_textbox("htmldir", $d->{'public_html_dir'}, 20));
	}

# Redirect non-SSL to SSL?
if (&domain_has_ssl($d) && &can_edit_redirect() && &has_web_redirects($d)) {
	my @redirects = map { &remove_wellknown_redirect($_) }
			    &list_redirects($d);
	my ($defredir) = grep { $_->{'path'} eq '/' &&
			        $_->{'http'} && !$_->{'https'} } @redirects;
	print &ui_table_row(&hlink($text{'phpmode_sslredir'}, 'sslredir'),
		&ui_yesno_radio("sslredir", $defredir ? 1 : 0));
	}

print &ui_hidden_table_end();

# Show PHP information
if (defined(&list_php_modules) && !$d->{'alias'}) {
	print &ui_hidden_table_start($text{'phpmode_header2'}, "width=100%",
				     2, "phpinfo", 0, [ "width=30%" ]);

	# PHP versions
	foreach $phpver (&list_available_php_versions($d)) {
		my $fullver = $phpver->[1] ? &get_php_version($phpver->[1], $d)
					   : $phpver->[0];
		push(@vlist, $fullver);
		}
	print &ui_table_row($text{'phpmode_vers'},
		@vlist ? join(", ", @vlist) : $text{'phpmode_novers'});

	# PHP errors for the domain
	foreach $phpver (&list_available_php_versions($d)) {
		$errs = &check_php_configuration($d, $phpver->[0],$phpver->[1]);
		if ($errs) {
			print &ui_table_row(&text('phpmode_errs', $phpver->[0]),
			    "<font color=red>".&html_escape($errs)."</font>");
			}
		}

	# PHP modules for the domain
	foreach $phpver (&list_available_php_versions($d)) {
		@mods = &list_php_modules($d, $phpver->[0], $phpver->[1]);
		@mods = sort { lc($a) cmp lc($b) } @mods;
		if (@mods) {
			print &ui_table_row(&text('phpmode_mods', $phpver->[0]),
				&ui_grid_table([ map { "<tt>$_</tt>" } @mods ],
					       6, 100));
			}
		}

	# Pear modules
	if (&foreign_check("php-pear")) {
		&foreign_require("php-pear");
		@allmods = ( );
		if (defined(&php_pear::list_installed_pear_modules)) {
			@allmods = &php_pear::list_installed_pear_modules();
			}
		@cmds = ( );
		if (defined(&php_pear::get_pear_commands)) {
			@cmds = &php_pear::get_pear_commands();
			}
		foreach $cmd (@cmds) {
			@mods = grep { $_->{'pear'} == $cmd->[1] } @allmods;
			@mods = sort { lc($a->{'name'}) cmp lc($b->{'name'}) }
				     @mods;
			if (@mods) {
				print &ui_table_row(
				    &text('phpmode_pears', $cmd->[1]),
				    &ui_grid_table(
				      [ map { "<tt>$_->{'name'}</tt>" } @mods ], 6, 100));
				}
			}
		}

	print &ui_hidden_table_end();
	}

print &ui_form_end([ [ "save", $text{'save'} ] ]);

&ui_print_footer(&domain_footer_link($d),
		 "", $text{'index_return'});

