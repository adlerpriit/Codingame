use strict;
use warnings;
use diagnostics;
use 5.20.1;
use Math::Trig;

select(STDOUT); $| = 1; # DO NOT REMOVE

# Send your busters out into the fog to trap ghosts and bring them home!
chomp(my $busters_count = <STDIN>); # the amount of busters you control
chomp(my $ghost_count = <STDIN>); # the amount of ghosts on the map
chomp(my $myTID = <STDIN>); # if this is 0, your base is on the top left of the map, if it is one, on the bottom right
our $base = ($myTID == 0 ? [0,0] : [16000,9000]);
our $oase = ($myTID == 1 ? [0,0] : [16000,9000]);

sub getDist($$) {
    my ($a,$b) = @_;
    my $dist = int(sqrt( ($a->[0] - $b->[0])**2 + ($a->[1] - $b->[1])**2 ));
    return($dist);
}

sub getDest($$$) {
    # $a has to be the point from which we want to have the distance and $b would in this case always be our buster
    my ($a,$b,$d) = @_;
    my $z = getDist($a,$b);
    if ($z==0) {
        $b->[0] = ($b->[0] < 9000 ? $b->[0] + 1 : $b->[0] - 1);
        $b->[1] = ($b->[1] < 4500 ? $b->[1] + 1 : $b->[1] - 1);
        $z = getDist($a,$b);
    }
    my $x = int($a->[0] - (($d * ($a->[0] - $b->[0]))/$z));
    my $y = int($a->[1] - (($d * ($a->[1] - $b->[1]))/$z));
    if ($x < 0) {
        $y = ($a->[1] < $b->[1] ? $y - $x : $y + $x);
        $x = 0 ;
    } elsif ($x > 16000) {
        $y = ($a->[1] < $b->[1] ? $y - (16000-$x) : $y + (16000-$x));
        $x = 16000 ;
    }
    if ($y < 0) {
        $x = ($a->[0] < $b->[0] ? $x - $y : $x + $y);
        $y = 0 ;
    } elsif ($y > 9000) {
        $x = ($a->[0] < $b->[0] ? $x - (9000-$y) : $x + (9000-$y));
        $y = 9000 ;
    }
    return([$x,$y]);
}

sub getAvoidDest($$$) {
    my ($a,$b,$c) = @_;
    #a is opponent position
    #b is my position
    #c is my base
    my $d_ab = getDist($a,$b) || 1;
    my $d_ac = getDist($a,$c);
    my $d_bc = getDist($b,$c);
    my $angle_from_oppo = int(rad2deg(atan2($b->[1] - $a->[1], $b->[0] - $a->[0])));
    my $angle_from_base = int(rad2deg(atan2($b->[1] - $c->[1], $b->[0] - $c->[0])));
    my $sp = $d_ab + 799 - 2560;
       $sp = ($sp > 20 ? $sp : 20); #this only happens if I cannot stun and have to risk running anyway
    my $op_w = ($d_bc - $d_ac) / $d_ab;
    my $deg_corr = int(((100/440) * $sp)); #$op_w
    
    my $angle = $angle_from_oppo;
    #final angle to get
    if($op_w < 0) {
        #opponent is further away from me
        #turn more toward base
        $op_w = 1 + $op_w;
        $deg_corr = int($deg_corr * $op_w);
        $angle = ($angle_from_oppo < $angle_from_base ? ($angle_from_oppo - $deg_corr) : ($angle_from_oppo + $deg_corr))
    } else {
        $angle = (($angle_from_base > 45 and $angle_from_oppo > 0) ? ($angle_from_oppo - $deg_corr) : ($angle_from_oppo + $deg_corr));
    }
    my $x = int(cos(deg2rad($angle)) * 850) + $b->[0];
    my $y = int(sin(deg2rad($angle)) * 850) + $b->[1];
        
    print STDERR "AVOID INFO: ",$angle_from_base,":",$angle_from_oppo,"(",$deg_corr,":",$angle,") angles with ",$sp," to spare and ",$op_w," weight\n";
    if ($x < 0) {
        $y = ($a->[1] < $b->[1] ? $y - $x : $y + $x);
        $x = 0 ;
    } elsif ($x > 16000) {
        $y = ($a->[1] < $b->[1] ? $y - (16000-$x) : $y + (16000-$x));
        $x = 16000 ;
    }
    if ($y < 0) {
        $x = ($a->[0] < $b->[0] ? $x - $y : $x + $y);
        $y = 0 ;
    } elsif ($y > 9000) {
        $x = ($a->[0] < $b->[0] ? $x - (9000-$y) : $x + (9000-$y));
        $y = 9000 ;
    }
    return([$x,$y]);
}

sub initPois() {
    my %pois = () ;
    for my $x (0..8) {
        for my $y (0..4) {
            if ($x+$y > 1 and $x+$y < 12) {
                $pois{"$x $y"} = [$x*2000,$y*2250];
            }
        }
    }
    return(\%pois);
}

sub getVisOppo($$$) {
    my ($oppo_ref,$ovis_ref,$buster) = @_;
    my $d = 2201;
    my $r = undef;
    for my $oid (keys%$ovis_ref) {
        my $d_from = getDist($oppo_ref->{$oid}->{'p'},$buster->{'p'});
        if ($d_from < $d and $oppo_ref->{$oid}->{'s'} != 2) {
            print STDERR "OVIS: ",$oid," - ", $d_from,"\n";
            $r = $oid;
            $d = $d_from;
        }
    }
    return({'id'=>$r,'d'=>$d});
}

sub getVisOppoAll($$$) {
    my ($oppo_ref,$ovis_ref,$buster) = @_;
    my $d = 2201;
    my $r = undef;
    for my $oid (keys%$ovis_ref) {
        my $d_from = getDist($oppo_ref->{$oid}->{'p'},$buster->{'p'});
        if ($d_from < $d) {
            print STDERR "OVIS: ",$oid," - ", $d_from,"\n";
            $r = $oid;
            $d = $d_from;
        }
    }
    return({'id'=>$r,'d'=>$d});
}


sub interceptOppo($$$$$$) {
    my ($oppo_ref,$ovis_ref,$gois_ref,$stun,$help_me_ref,$buster) = @_;
    return(undef) if $buster->{'s'} == 2 ;
    my @targets = () ;    #hunt opponents carrying a ghost
    my %dists = () ;
    my $d_from_oase = getDist($oase,$buster->{'p'});
    for my $oid (keys%$oppo_ref) {
        push @targets, $oid if $oppo_ref->{$oid}{'s'} == 1;
        $dists{$oid}{'me'} = getDist($oppo_ref->{$oid}{'p'},$buster->{'p'});
        $dists{$oid}{'ob'} = getDist($oppo_ref->{$oid}{'p'},$oase);
        for my $hbid (keys%$help_me_ref) {
            if ($oid eq $help_me_ref->{$hbid}) {
                print STDERR "GO GET ",$oid,"\n";
                return({'id'=>$oid,'d'=>$dists{$oid}{'me'},'dest'=>$oppo_ref->{$oid}{'p'}});
            }
        }
        if ($dists{$oid}{'me'} < 1760 and not defined($stun->{"B".$buster->{'id'}}) and not defined($stun->{$oid})) {
            unless ($buster->{'s'}==3 and $gois_ref->{"G".$buster->{'v'}}{'s'} > 6) {
                print STDERR "STUN:",$oid," - ",$oppo_ref->{$oid}{'s'},"(",$dists{$oid}{'me'},")\n";
                return({'id'=>$oid,'d'=>$dists{$oid}{'me'},'dest'=>$oppo_ref->{$oid}{'p'}});
            }
        }
    }
    #sort targets based on distance from their base
    @targets = sort {
        $dists{$a}{'ob'} <=> $dists{$b}{'ob'} || $dists{$a}{'me'} <=> $dists{$b}{'me'}
    } @targets;
    for my $oid (@targets) {
        my $my_d = int($d_from_oase / 800) - 4 ;
        my $op_d = int($dists{$oid}{'ob'} / 800) - 2;
        print STDERR "TARGET:",$oid," - ",$oppo_ref->{$oid}{'s'},"(",$op_d,":",$my_d,")\n";
        if (not defined($stun->{"B".$buster->{'id'}}) or $stun->{"B".$buster->{'id'}}{'t'} < $op_d + 1) {
            my $isOnLine = $d_from_oase + $dists{$oid}{'me'} - $dists{$oid}{'ob'};
            if ((defined($ovis_ref->{$oid}) and $dists{$oid}{'me'} < 2400) or $isOnLine < 500) {
                my $dest = getDest($oase,$oppo_ref->{$oid}{'p'},$dists{$oid}{'ob'} - 901);
                return({'id'=>$oid,'d'=>$dists{$oid}{'me'},'dest'=>$dest})
            }
            if ( $my_d <= $op_d) {
                my $diff = $op_d - $my_d ;
                my $dest = getDest($oase,$oppo_ref->{$oid}{'p'},1600 + 800*$diff);
                return({'id'=>$oid,'d'=>$dists{$oid}{'me'},'dest'=>$dest})
            }
        }
    }
    return(undef);
}

sub getWeakest($$$$) {
    my ($gois_ref, $gvis_ref, $pois, $buster) = @_;
    my @slist = sort {$gois_ref->{$a}{'s'} <=> $gois_ref->{$b}{'s'}} keys%$gois_ref;
    if (scalar@slist == 0) {
        return(undef);
    }
    my $r = $slist[0];
    my $s = $gois_ref->{$r}{'s'};
    my $d = getDist($gois_ref->{$r}{'p'},$buster->{'p'});
    if ($s == 0) {
        if ($buster->{'s'} == 3 and $gois_ref->{"G".$buster->{'v'}}{'s'} > 10) {
            print STDERR "EARLY RETURN\n";
            return({'id'=>$r,'d'=>$d,'s'=>$s});
        }
    }
    #print STDERR "LIST: '",join(":",@slist),"'\n";
    for my $gid (@slist) {
        my $d_from = getDist($gois_ref->{$gid}{'p'},$buster->{'p'});
        if ($d_from < 2200 and not defined($gvis_ref->{$gid})) {
            my @goi = @{$gois_ref->{$gid}{'p'}} ;
            print STDERR "removing ",$gid," from gois and adding to pois: ",join(" ",@goi),"\n";
            $pois->{$gid} = \@goi;
            delete($gois_ref->{$gid});
        } else {
            #print STDERR "G '",sprintf("%3s",$gid),"' - ",$d_from,":",$gois_ref->{$gid}{'s'},"\n";
            if ($s + 5 < $gois_ref->{$gid}{'s'} and defined($gois_ref->{$r})) {
                return({'id'=>$r,'d'=>$d,'s'=>$s});
            }
            if ($d_from < $d) {
                $d = $d_from;
                $r = $gid;
            }
        }
    }
    if (defined($gois_ref->{$r})) {
        
        return({'id'=>$r,'d'=>$d,'s'=>$s});
    } else {
        return(undef);
    }
}

sub getPoi($$$) {
    my ($pois,$apoi,$buster) = @_;
    my @pois = keys%$pois;
    if(scalar@pois==0 or $buster->{'s'}==3) {
        return(undef);
    }
    my $poi = undef;
    my $goi = undef;
    my $toPoi = 999999;
    my $toGoi = 999999;
    for my $pid (@pois) {
        my $d_to = getDist($pois->{$pid},$buster->{'p'});
        if (($d_to < 2150 and $pid !~ m[G]) or ($d_to < 450 and $pid =~ m[G])) {
            #print STDERR "DELETE POI: ",$pid,"\n";
            delete($pois->{$pid});
        } else {
            if ($pid =~ m[G] and $d_to < $toGoi and !defined($apoi->{$pid})) {
                $toGoi = $d_to;
                $goi = $pid;
            }
            if ($pid !~ m[G] and $d_to < $toPoi and !defined($apoi->{$pid})) {
                $toPoi = $d_to;
                $poi = $pid;
            }
        }
    }
    $poi = ($poi ? $poi : $goi);
    $apoi->{$poi} = "taken" if $poi and $buster->{'s'} != 2 ;
    return($poi);
}

sub reduceStun($) {
    my $stun = shift;
    my @ids = keys%$stun ;
    for my $id (@ids) {
        if ($stun->{$id}{'t'} == 0) {
            delete($stun->{$id});
        } else {
            $stun->{$id}{'t'} -= 1;
        }
    }
}

sub updateInvisibleOppo($$) {
    my ($oppo_ref,$ovis_ref) = @_;
    for my $oid (keys%$oppo_ref) {
        if (not defined($ovis_ref->{$oid})) {
            my $d_from_oase = getDist($oppo_ref->{$oid}{'p'},$oase);
            $oppo_ref->{$oid}{'p'} = getDest($oase,$oppo_ref->{$oid}{'p'},$d_from_oase - 790);
        }
    }
}

my $tokens;

my %gois = ();
my %team = ();
my %oppo = ();

my $pois = initPois();
my %stun = ();
my $busted_count = 0 ;
my %help_me = ();
print STDERR "Ghosts in play: ",$ghost_count,"\n";
# game loop
while (1) {
    reduceStun(\%stun);
    print STDERR "STUN: '",join(" ",keys%stun),"'\n";
    my %gvis = (); #visible ghosts
    my %ovis = (); #visible opponents
    my $apoi = {}; #allocated pois
    my $carry_count = 0 ;
    chomp(my $entities = <STDIN>); # the number of busters and ghosts visible to you
    for my $i (0..$entities-1) {
        # entity_id: buster id or ghost id
        # y: position of this buster / ghost
        # entity_type: the team id if it is a buster, -1 if it is a ghost.
        # state: For busters: 0=idle, 1=carrying a ghost. For ghosts: remaining stamina points.
        # value: For busters: Ghost id being carried/busted or number of turns left when stunned. For ghosts: number of busters attempting to trap this ghost.
        chomp($tokens=<STDIN>);
        my ($eid, $x, $y, $etype, $state, $value) = split(/ /,$tokens);
        if ($etype == $myTID) {
            $team{"B".$eid} = {'id'=>$eid,'p'=>[$x,$y],'s'=>$state,'v'=>$value};
            if ($state == 1) {
                $carry_count += 1;
            } elsif ($state != 1 and defined($help_me{"B".$eid})) {
                delete($help_me{"B".$eid})
            }
        } elsif ($etype == -1) {
            $gvis{"G".$eid} = "visible";
            $gois{"G".$eid} = {'id'=>$eid,'p'=>[$x,$y],'s'=>$state,'v'=>$value};
        } else {
            $ovis{"O".$eid} = "visible";
            $oppo{"O".$eid} = {'id'=>$eid,'p'=>[$x,$y],'s'=>$state,'v'=>$value};
            if (defined($stun{"O".$eid}) and $state != 2 and $stun{$stun{"O".$eid}{'id'}}{'t'} > 15) {
                delete($stun{$stun{"O".$eid}{'id'}});
                delete($stun{"O".$eid});
            } elsif (defined($stun{"O".$eid}) and $state == 2) {
                $stun{"O".$eid}{'t'} = $value;
            }
        }
    }
        
    print STDERR "GVIS: '",join(":",keys%gvis),"'\n";
    for my $bid (sort {$a cmp $b} keys%team) {
        print STDERR "ID: ",$bid," - ",$team{$bid}{'s'}," pos:",join(" ",@{$team{$bid}{'p'}}),"\n";
        if ($team{$bid}{'s'} == 2 and not defined($stun{$bid})) {
            $stun{$bid}{'t'} = $team{$bid}{'v'};
        }
        my $isStun = (defined($stun{$bid}) ? " W".$stun{$bid}{'t'}."\n" : "\n");
        my $poi = getPoi($pois,$apoi,$team{$bid});
        #actions
        #if carrying ghost, bring it to base
        if ($team{$bid}{'s'} == 1) {
            if(defined($gois{"G".$team{$bid}{'v'}})) {
                delete($gois{"G".$team{$bid}{'v'}});
            }
            my $d = getDist($base,$team{$bid}{'p'});
            if( $d < 1600) {
                print("RELEASE".$isStun);
                $busted_count += 1;
                if (defined($help_me{$bid})) {delete($help_me{$bid})}
            } else {
                my $oid = getVisOppo(\%oppo,\%ovis,$team{$bid});
                if ($oid->{'id'}) {
                    $help_me{$bid} = $oid->{'id'} ;
                    my $dist = getDist($oppo{$oid->{'id'}}{'p'},$team{$bid}{'p'});
                    if ($dist < 1760 and not defined($stun{$oid->{'id'}}) and not defined($stun{$bid})) {
                        print("STUN ".$oppo{$oid->{'id'}}{'id'}." S1 ".$oid->{'id'}.$isStun);
                        $stun{$bid}{'t'} = 19;
                        $stun{$oid->{'id'}}{'t'} = 9;
                        $stun{$oid->{'id'}}{'id'} = $bid;
                    } else {
                        my $dest = getAvoidDest($oppo{$oid->{'id'}}{'p'},$team{$bid}{'p'},$base);
                        #my $dest = getDest($oppo{$oid->{'id'}}{'p'},$team{$bid}{'p'},800 + $dist);
                        print("MOVE ".(join(" ",@$dest))." A ".$oid->{'id'}.$isStun);
                    }
                } else {
                    if (defined($help_me{$bid})) {delete($help_me{$bid})}
                    my $dest = getDest($base,$team{$bid}{'p'},1500);
                    if ($ghost_count/2 <= $busted_count + $carry_count) {
                        $oid = getVisOppoAll(\%oppo,\%ovis,$team{$bid});
                        if ($oid->{'id'}) {
                            $dest = getAvoidDest($oppo{$oid->{'id'}}{'p'},$team{$bid}{'p'},$base);
                        } else {
                            $dest = $team{$bid}{'p'} ;
                        }
                        print STDERR "WAITING/HIDING\n";
                        $isStun = " not yet".$isStun;
                    }
                    print("MOVE ".(join(" ",@$dest))." B".$isStun);
                }
            }
            next;
        }
        #battle with opponent
        my $oid = interceptOppo(\%oppo,\%ovis,\%gois,\%stun,\%help_me,$team{$bid});
        my $gid = getWeakest(\%gois,\%gvis,$pois,$team{$bid});
        if ($oid->{'id'} and (!$gid or $gid->{'s'} != 0)) {
            if ($oid->{'d'} < 1760 and not defined($stun{$bid}) and not defined($stun{$oid->{'id'}})) {
                print("STUN ".$oppo{$oid->{'id'}}{'id'}." S2 ".$oid->{'id'}.$isStun);
                $stun{$bid}{'t'} = 19;
                $stun{$oid->{'id'}}{'t'} = 9;
                $stun{$oid->{'id'}}{'id'} = $bid;
                if ($oppo{$oid->{'id'}}{'s'} == 1) {
                    $gois{"G".$oppo{$oid->{'id'}}{'v'}} = {'id'=>$oppo{$oid->{'id'}}{'v'},'p'=>$oppo{$oid->{'id'}}{'p'},'s'=>0,'v'=>0};
                }
            } else {
                print("MOVE ".join(" ",@{$oid->{'dest'}})." O ".$oid->{'id'}.$isStun);
            }
            next;
        }
        #go for the weakest ghost
        #explore and get the weakest ghosts
        if ($poi and (!$gid or $gid->{'s'} > 10)) {
            print STDERR "POI: ",$poi,"\n";
            if (($poi =~ m[G] and !$gid) or $poi !~ m[G]) {
                print("MOVE ".(join(" ",@{$pois->{$poi}}))." POI ".$poi.$isStun);
                next;
            }
        }
        if ($gid) {
            print STDERR "returned: ",$gid->{'id'},"\n";
            if ($gid->{'d'} > 900 and $gid->{'d'} < 1755 and defined($gvis{$gid->{'id'}})) {
                print("BUST ".$gois{$gid->{'id'}}{'id'}." B ".$gid->{'id'}.$isStun);
            } else {
                my $dest = getDest($gois{$gid->{'id'}}{'p'},$team{$bid}{'p'},950);
                print("MOVE ".(join(" ",@$dest))." G ".$gid->{'id'}.$isStun);
            }
        } else {
            #nothing left, if game is not over, go hunt opponent base
            my $dest = getDest($oase,$team{$bid}{'p'},1600);
            print("MOVE ".(join(" ",@$dest))." EOL".$isStun);
        }
    }
    updateInvisibleOppo(\%oppo,\%ovis);
}