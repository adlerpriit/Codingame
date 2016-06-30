use strict;
use warnings;
#use diagnostics;
use 5.20.1;

select(STDOUT); $| = 1; # DO NOT REMOVE

# Send your busters out into the fog to trap ghosts and bring them home!

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
    my ($oppo,$ovis,$b) = @_;
    my $d = 2201;
    my $r = undef;
    for my $oid (keys%$ovis) {
        $d_from = getDist($oppo->{$oid}->{'p'},$b->{'p'});
        if ($d_from < $d and $oppo->{$oid}->{'s'} != 2) {
            $r = $oid;
            $d = $d_from;
        }
    }
    return({'id'=>$r,'d'=>$d});
}

sub getWeakest($$$$) {
    my ($gois, $gvis, $pois, $b) = @_;
    my @slist = sort {$gois->{$a}->{'s'} <=> $gois->{$b}->{'s'}} keys%$gois;
    if (scalar@slist == 0) {
        return(undef);
    }
    my $r = $slist[0];
    my $s = $gois->{$r}->{'s'};
    my $d = getDist($gois->{$r}->{'p'},$b->{'p'});
    if ($s == 0) {
        if ($b->{'s'} == 3 and $gois->{$b->{'v'}}->{'s'} > 10) {
            return({'id'=>$r,'d'=>$d});
        }
    }
    for my $gid (@slist) {
        my $d_from = getDist($gois->{$gid}->{'p'},$b->{'p'});
        if ($d_from < 2200 and !defined($gvis->{$r})) {
            $pois->{"G $gid"} = $gois->{$gid}->{'p'};
            delete($gois->{$gid});
        } else {
            if ($s + 10 < $gois->{$gid}->{'s'}) {
                return({'id'=>$r,'d'=>$d});
            }
            if ($d_from < $d) {
                $d = $d_from;
                $r = $gid;
            }
        }
    }
    return({'id'=>$r,'d'=>$d});
}

sub getPoi($$$) {
    my ($pois,$apoi,$b) = @_;
    my @pois = keys%$pois;
    if(scalar@pois==0) {
        return(undef);
    }
    my $poi = @pois[0];
    my $toPoi = getDist($pois->{$poi},$b->{'p'});
    for my $pid (@pois) {
        $d_to = getDist($pois->{$pid},$b->{'p'});
        if ($d_to < 2100) {
            delete($pois->{$pid})
        } else {
            if ($d_to < $toPoi and !defined($apoi->{$pid})) {
                $toPoi = $d_to;
                $poi = $pid;
            }
        }
    }
    $apoi->{$poi} = "taken";
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

chomp(my $busters_count = <STDIN>); # the amount of busters you control
chomp(my $ghost_count = <STDIN>); # the amount of ghosts on the map
chomp(my $myTID = <STDIN>); # if this is 0, your base is on the top left of the map, if it is one, on the bottom right
my $base = ($myTID == 0 ? [0,0] : [16000,9000]);
my $oase = ($myTID == 1 ? [0,0] : [16000,9000]);

my %gois = ();
my %team = ();
my %oppo = ();

my $pois = initPois();
my %stun = ();
# game loop
while (1) {
    reduceStun(\%stun)
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
            $team{$eid} = {'p'=>[$x,$y],'s'=>$state,'v'=>$value};
        } elsif ($etype == -1) {
            $gvis{$eid} = "visible";
            $gois{$eid} = {'p'=>[$x,$y],'s'=>$state,'v'=>$value};
        } else {
            $ovis{$eid} = "visible";
            if ($state != 2) {
                $oppo{$eid} = {'p'=>[$x,$y],'s'=>$state,'v'=>$value};
            }
        }
    }
    for my $bid (sort keys%team) {
        my $isStun = (defined($stun{$bid}) ? " W".$stun{$bid} ? "");
        my $poi = getPoi($pois,$apoi,$team{$bid});
        #actions
        #if carrying ghost, bring it to base
        if ($team{$bid}{'s'} == 1) {
            if(defined($gois{$team{$bid}{'v'}})) {
                delete($gois{$team{$bid}{'v'}});
            }
            my $d = getDist($base,$team{$bid}{'p'});
            if( $d < 1600) {
                print("RELEASE");
            } else {
                my $oid = getVisOppo(\%oppo,\%ovis,$team{$bid});
                if ($oid->{'id'}) {
                    my $dest = getDest($oppo{$oid->{'id'}}{'p'},$team{$bid}{'p'},3000);
                    print("MOVE ".(join(" ",@$dest))." A ".$oid->{'id'});
                } else {
                    my $dest = getDest($base,$team{$bid}{'p'},1500);
                    print("MOVE ".(join(" ",@$dest))." B");
                }
            }
            next;
        }
        my $oid = interceptOppo(%oppo,%ovis,$team{$bid});
        if ($oid->{'id'}) {
            if ($oid->{'d'} < 1760 and !defined($stun{$bid})) {
                print("STUN ".$oid->{'id'}." S ".$oid->{'id'});
            } else {
                print("MOVE ".join(" ",@{$oid->{'dest'}})." O ".$oid->{'id'});
            }
            next;
        }
        my $gid = getWeakest(\%gois,\%gvis,$pois,$team{$bid});
        
        #battle with opponent
        #explore and get the weakest ghosts
        #go for the weakest ghost
        #if noting else to to go to opponent base
    }
}
