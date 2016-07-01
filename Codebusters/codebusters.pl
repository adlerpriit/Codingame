use strict;
use warnings;
use diagnostics;
use 5.20.1;

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
        $b->[0] = ($b->[0] < 15000 ? $b->[0] + 1 : $b->[0] - 1);
        $b->[1] = ($b->[1] < 8000 ? $b->[1] + 1 : $b->[1] - 1);
        $z = getDist($a,$b);
    }
    my $x = int($a->[0] - (($d * ($a->[0] - $b->[0]))/$z));
    my $y = int($a->[1] - (($d * ($a->[1] - $b->[1]))/$z));
    return([$x,$y]);
}

sub initPois() {
    my %pois = () ;
    for my $x (0..16) {
        for my $y (0..9) {
            if ($x+$y > 4 and $x+$y < 21) {
                $pois{"$x $y"} = [$x*1000,$y*1000];
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
        print STDERR "OVIS: ",$oid," - ", $d_from,"\n";
        if ($d_from < $d and $oppo_ref->{$oid}->{'s'} != 2) {
            $r = $oid;
            $d = $d_from;
        }
    }
    return({'id'=>$r,'d'=>$d});
}

sub interceptOppo($$$$) {
    my ($oppo_ref,$ovis_ref,$stun,$buster) = @_;
    my @targets = () ;    #hunt opponents carrying a ghost
    my %dists = () ;
    my $d_from_oase = getDist($oase,$buster->{'p'});
    for my $oid (keys%$oppo_ref) {
        push @targets, $oid if $oppo_ref->{$oid}{'s'} == 1;
        $dists{$oid}{'me'} = getDist($oppo_ref->{$oid}{'p'},$buster->{'p'});
        $dists{$oid}{'ob'} = getDist($oppo_ref->{$oid}{'p'},$oase);
    }
    #sort targets based on distance from their base
    @targets = sort {
        $dists{$a}{'ob'} <=> $dists{$b}{'ob'} || $dists{$a}{'me'} <=> $dists{$b}{'me'}
    } @targets;
    for my $oid (@targets) {
        print STDERR "TARGET:",$oid," - ",$oppo_ref->{$oid}{'s'},"\n";
        my $my_d = int($d_from_oase / 800);
        my $op_d = int($dists{$oid}{'ob'} / 800);
        if ( $my_d+1 <= $op_d and (not defined($stun->{"B".$buster->{'id'}}) or $stun->{"B".$buster->{'id'}} < $op_d)) {
            my $dest = getDest($oase,$oppo_ref->{$oid}{'p'},1800);
            return({'id'=>$oid,'d'=>$dists{$oid}{'me'},'dest'=>$dest})
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
    print STDERR "LIST: '",join(":",@slist),"'\n";
    for my $gid (@slist) {
        my $d_from = getDist($gois_ref->{$gid}{'p'},$buster->{'p'});
        if ($d_from < 2200 and not defined($gvis_ref->{$gid})) {
            my @goi = @{$gois_ref->{$gid}{'p'}} ;
            print STDERR "removing ",$gid," from gois and adding to pois: ",join(" ",@goi),"\n";
            $pois->{$gid} = \@goi;
            delete($gois_ref->{$gid});
        } else {
            if ($s + 15 < $gois_ref->{$gid}{'s'} and defined($gois_ref->{$r})) {
                return({'id'=>$r,'d'=>$d,'s'=>$s});
            }
            print STDERR "G '",sprintf("%3s",$gid),"' - ",$d_from,":",$s,"\n";
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
    if(scalar@pois==0) {
        return(undef);
    }
    my $poi = undef;
    my $toPoi = 999999;
    for my $pid (@pois) {
        my $d_to = getDist($pois->{$pid},$buster->{'p'});
        if ($d_to < 2100) {
            print STDERR "DELETE POI: ",$pid,"\n";
            delete($pois->{$pid})
        } else {
            if ($d_to < $toPoi and !defined($apoi->{$pid})) {
                $toPoi = $d_to;
                $poi = $pid;
            }
        }
    }
    $apoi->{$poi} = "taken" if $poi;
    return($poi);
}

sub reduceStun($) {
    my $stun = shift;
    my @ids = keys%$stun ;
    for my $id (@ids) {
        if ($stun->{$id} == 0) {
            delete($stun->{$id});
        } else {
            $stun->{$id} -= 1;
        }
    }
}

my $tokens;

my %gois = ();
my %team = ();
my %oppo = ();

my $pois = initPois();
my %stun = ();
# game loop
while (1) {
    reduceStun(\%stun);
    print STDERR "STUN: '",join(" ",keys%stun),"'\n";
    my %gvis = (); #visible ghosts
    my %ovis = (); #visible opponents
    my $apoi = {}; #allocated pois
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
            $team{"B".$eid} = {'p'=>[$x,$y],'s'=>$state,'v'=>$value};
        } elsif ($etype == -1) {
            $gvis{"G".$eid} = "visible";
            $gois{"G".$eid} = {'id'=>$eid,'p'=>[$x,$y],'s'=>$state,'v'=>$value};
        } else {
            $ovis{"O".$eid} = "visible";
            if ($state != 2) {
                $oppo{"O".$eid} = {'id'=>$eid,'p'=>[$x,$y],'s'=>$state,'v'=>$value};
            }
        }
    }
    for my $bid (sort {$a cmp $b} keys%team) {
        print STDERR "ID: ",$bid," - ",$team{$bid}{'s'},"\n";
        if ($team{$bid}{'s'} == 2) {
            $stun{$bid} = $team{$bid}{'v'};
        }
        my $isStun = (defined($stun{$bid}) ? " W".$stun{$bid}."\n" : "\n");
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
            } else {
                my $oid = getVisOppo(\%oppo,\%ovis,$team{$bid});
                if ($oid->{'id'}) {
                    my $dist = getDist($oppo{$oid->{'id'}}{'p'},$team{$bid}{'p'});
                    if ($dist < 1760 and not defined($stun{$oid->{'id'}})) {
                        print("STUN ".$oppo{$oid->{'id'}}{'id'}." S1 ".$oid->{'id'}.$isStun);
                        $stun{$bid} = 19;
                        $stun{$oid->{'id'}} = 9;
                    } else {
                        my $dest = getDest($oppo{$oid->{'id'}}{'p'},$team{$bid}{'p'},800 + $dist);
                        print("MOVE ".(join(" ",@$dest))." A ".$oid->{'id'}.$isStun);
                    }
                } else {
                    my $dest = getDest($base,$team{$bid}{'p'},1500);
                    print("MOVE ".(join(" ",@$dest))." B".$isStun);
                }
            }
            next;
        }
        #battle with opponent
        my $oid = interceptOppo(\%oppo,\%ovis,\%stun,$team{$bid});
        if ($oid->{'id'}) {
            if ($oid->{'d'} < 1760 and not defined($stun{$bid}) and not defined($stun{$oid->{'id'}})) {
                print("STUN ".$oppo{$oid->{'id'}}{'id'}." S2 ".$oid->{'id'}.$isStun);
                $stun{$bid} = 19;
                $stun{$oid->{'id'}} = 9;
            } else {
                print("MOVE ".join(" ",@{$oid->{'dest'}})." O ".$oid->{'id'}.$isStun);
            }
            next;
        }
        #go for the weakest ghost
        my $gid = getWeakest(\%gois,\%gvis,$pois,$team{$bid});
        if ($gid) {
            $gid->{'s'} = $gois{$gid->{'id'}}{'s'};
            print STDERR "returned: ",$gid->{'id'},"\n";
        }
        #explore and get the weakest ghosts
        if ($poi and (!$gid or $gid->{'s'} > 10)) {
            #print STDERR "POI: ",$poi,"\n";
            print("MOVE ".(join(" ",@{$pois->{$poi}}))." POI ".$poi.$isStun);
            next;
        }
        if ($gid) {
            if ($gid->{'d'} > 900 and $gid->{'d'} < 1755 and defined($gvis{$gid->{'id'}})) {
                print("BUST ".$gois{$gid->{'id'}}{'id'}." B ".$gid->{'id'}.$isStun);
            } else {
                my $dest = getDest($gois{$gid->{'id'}}{'p'},$team{$bid}{'p'},901);
                print("MOVE ".(join(" ",@$dest))." G ".$gid->{'id'}.$isStun);
            }
        } else {
            #nothing left, if game is not over, go hunt opponent base
            my $dest = getDest($oase,$team{$bid}{'p'},1600);
            print("MOVE ".(join(" ",@$dest))." EOL".$isStun);
        }
    }
}
