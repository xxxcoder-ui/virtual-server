#!/usr/bin/perl
# Copy this domain's cert to Dovecot

require './virtual-server-lib.pl';
&ReadParse();
$d = &get_domain($in{'dom'});
$d && &can_edit_domain($d) && &can_edit_ssl() && &can_webmin_cert() ||
	&error($text{'copycert_ecannot'});
$d->{'ssl_pass'} && &error($text{'copycert_epass'});

&ui_print_header(&domain_in($d), $text{'copycert_title'}, "");

&copy_dovecot_ssl_service($d);
&run_post_actions();
&webmin_log("copycert", "dovecot");

&ui_print_footer("cert_form.cgi?dom=$d->{'id'}", $text{'cert_return'},
		 &domain_footer_link($d),
		 "", $text{'index_return'});

