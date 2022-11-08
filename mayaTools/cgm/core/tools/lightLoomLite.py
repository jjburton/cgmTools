"""
------------------------------------------
Light Loom Lite: cgm.core.tools
Authors: Matt Berenty | Josh Burton

Website : https://github.com/jjburton/cgmTools/wiki
------------------------------------------
================================================================
"""
__version__ = '0.1.01022019'
__MAYALOCAL = 'LIGHTLOOMLITE'


# From Python =============================================================
import copy
import re
import sys
import pprint
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# From Maya =============================================================
import maya.cmds as mc
import maya.mel as mel
from Red9.core import Red9_Meta as r9Meta

from cgm.core import cgm_Meta as cgmMeta
from cgm.core.cgmPy import validateArgs as VALID
from cgm.core import cgm_General as cgmGEN
from cgm.core.lib import snap_utils as SNAP
from cgm.core.lib import locator_utils as LOC
from cgm.core.lib import attribute_utils as ATTR
from cgm.core.lib import name_utils as NAMES
from cgm.core.lib import search_utils as SEARCH
import cgm.core.classes.GuiFactory as cgmUI
from cgm.core.tools.markingMenus.lib import contextual_utils as MMCONTEXT
import cgm.core.classes.GuiFactory as cgmUI
mUI = cgmUI.mUI

d_profiles = {'rimDark':{'back': {'dag': {'orient': [-134.3944379841386,
                             0.8019627216457283,
                             -17.177922380934522],
                  'position': [6.422550662070304,
                               22.688378227204286,
                               -8.002489006168625]},
          'settings': {'color': (1.0,
                                 0.8830000162124634,
                                 0.5550000071525574),
                       'emitDiffuse': True,
                       'emitSpecular': False,
                       'intensity': 0.2409638613462448},
          'type': 'directionalLight'},
 'back_left': {'dag': {'orient': [-143.8683322934451,
                                  0.39094760531390704,
                                  70.14716288793704],
                       'position': [-26.659771701008655,
                                    25.251568236270135,
                                    -18.35097052879612]},
               'settings': {'color': (1.2760000228881836,
                                      0.18950000405311584,
                                      0.0),
                            'emitDiffuse': True,
                            'emitSpecular': False,
                            'intensity': 1.5060241222381592},
               'type': 'directionalLight'},
 'back_right': {'dag': {'orient': [140.7344031345789,
                                   -37.018289629852596,
                                   92.44819354041762],
                        'position': [40.006773104060656,
                                     13.483893422412422,
                                     -14.020849167867775]},
                'settings': {'color': (0.0, 0.4120999872684479, 1.0),
                             'emitDiffuse': True,
                             'emitSpecular': False,
                             'intensity': 8.204819679260254},
                'type': 'directionalLight'},
 'key': {'dag': {'orient': [-30.526733697822817,
                            -31.64388861860398,
                            -86.09822424675464],
                 'position': [6.6687092906146725,
                              12.432645359314101,
                              42.332151963387574]},
         'settings': {'color': (1.0, 0.7455999851226807, 0.5),
                      'emitDiffuse': True,
                      'emitSpecular': False,
                      'intensity': 0.03999999910593033},
         'type': 'directionalLight'}},
              'rimMovie':{'backRight': {'dag': {'orient': [139.55467659581947,
                                  -1.0554341792773612,
                                  86.6052599757408],
                       'position': [0.0, 0.0, 0.0]},
               'settings': {'color': (1.100000023841858,
                                      0.4307999908924103,
                                      0.0),
                            'emitDiffuse': True,
                            'emitSpecular': False,
                            'intensity': 5.42168664932251},
               'type': 'directionalLight'},
 'back_left': {'dag': {'orient': [143.76420944223443,
                                  35.16030381093086,
                                  -62.680102807992895],
                       'position': [0.0, 0.0, 0.0]},
               'settings': {'color': (0.0,
                                      1.8055000305175781,
                                      6.924900054931641),
                            'emitDiffuse': True,
                            'emitSpecular': False,
                            'intensity': 3.433734893798828},
               'type': 'directionalLight'},
 'bottom': {'dag': {'orient': [-131.09701189254417,
                               76.14266665418256,
                               119.82127047738786],
                    'position': [0.0, 0.0, 0.0]},
            'settings': {'color': (1.0, 0.7762666940689087, 0.0),
                         'emitDiffuse': True,
                         'emitSpecular': False,
                         'intensity': 0.7228915691375732},
            'type': 'directionalLight'},
 'key': {'dag': {'orient': [-0.274732249767308,
                            -43.765528056509645,
                            -98.27257276442677],
                 'position': [0.0, 0.0, 0.0]},
         'settings': {'color': (0.9052000045776367, 0.5490000247955322, 1.0),
                      'emitDiffuse': True,
                      'emitSpecular': True,
                      'intensity': 0.5421686768531799},
         'type': 'directionalLight'}},
              'modeling1':{'back': {'dag': {'orient': [-154.44810095999918,
                             -8.04384821710512,
                             -6.070242264578304],
                  'position': [3.777222050783328,
                               19.105135357380576,
                               -15.5170193799141]},
          'settings': {'color': (1.0,
                                 0.8830000162124634,
                                 0.5550000071525574),
                       'emitDiffuse': True,
                       'emitSpecular': False,
                       'intensity': 0.0},
          'type': 'directionalLight'},
 'backLeft': {'dag': {'orient': [-154.19045921752925,
                                 19.776007292292952,
                                 78.13327476784856],
                      'position': [-27.999112431696158,
                                   11.843438629229858,
                                   -27.58488552382548]},
              'settings': {'color': (0.0, 0.559499979019165, 7.0),
                           'emitDiffuse': True,
                           'emitSpecular': False,
                           'intensity': 5.542168617248535},
              'type': 'directionalLight'},
 'backRight': {'dag': {'orient': [138.95220314637788,
                                  -15.21317918441351,
                                  103.07149140774418],
                       'position': [38.81347546972442,
                                    14.534724476555,
                                    -16.16160245045645]},
               'settings': {'color': (1.100000023841858,
                                      0.7000000476837158,
                                      0.0),
                            'emitDiffuse': True,
                            'emitSpecular': False,
                            'intensity': 5.6626505851745605},
               'type': 'directionalLight'},
 'bottom': {'dag': {'orient': [3.2309450528353323,
                               80.36321116578121,
                               -109.67848371077572],
                    'position': [-0.3022677675287601,
                                 -44.47875215464143,
                                 0.7005200764877779]},
            'settings': {'color': (0.8108879923820496,
                                   0.8536093831062317,
                                   0.9039999842643738),
                         'emitDiffuse': True,
                         'emitSpecular': False,
                         'intensity': 1.1000001430511475},
            'type': 'directionalLight'},
 'key': {'dag': {'orient': [-28.545365772012275,
                            -53.45974008296619,
                            -77.63853622962807],
                 'position': [0.109056460535216,
                              27.678931734027206,
                              34.99883267819116]},
         'settings': {'color': (1.0, 1.0, 1.0),
                      'emitDiffuse': True,
                      'emitSpecular': True,
                      'intensity': 1.5},
         'type': 'directionalLight'}},
              
'fireSide':
{'back': {'dag': {'orient': [-177.20251383025365,
                             -27.078687406777263,
                             83.76139478109735],
                  'position': [-54.69689857092704,
                               50.089696611917105,
                               -21.736595881908368]},
          'settings': {'color': (0.19599999487400055,
                                 0.33320000767707825,
                                 1.0),
                       'emitDiffuse': True,
                       'emitSpecular': False,
                       'intensity': 3.3734939098358154},
          'type': 'directionalLight'},
 'fill': {'dag': {'orient': [-5.883774546941699,
                             -69.2074613368921,
                             -157.4901512393294],
                  'position': [-27.311576918416357,
                               19.587066810605343,
                               -23.570486309704393]},
          'settings': {'color': (0.19599999487400055,
                                 0.33320000767707825,
                                 1.0),
                       'emitDiffuse': True,
                       'emitSpecular': False,
                       'intensity': 0.5421686768531799},
          'type': 'directionalLight'},
 'fire': {'dag': {'orient': [83.831212103383,
                             10.743467351798783,
                             -26.029250614729932],
                  'position': [-0.6609184097435603,
                               16.889365868808813,
                               -1.7945771140993645]},
          'settings': {'color': (1.0, 0.388866662979126, 0.0),
                       'emitDiffuse': True,
                       'emitSpecular': True,
                       'intensity': 0.9638554453849792},
          'type': 'directionalLight'},
 'key': {'dag': {'orient': [35.83264435800957,
                            -55.66177965039622,
                            -90.31392522446457],
                 'position': [-2.2349759945203047,
                              14.771271833833847,
                              42.046020677341744]},
         'settings': {'color': (0.0,
                                0.07349206507205963,
                                0.9409999847412109),
                      'emitDiffuse': True,
                      'emitSpecular': False,
                      'intensity': 1.5},
         'type': 'directionalLight'}}
,

'night':
{'bounce': {'dag': {'orient': [-20.57745119169334,
                               65.08640714385425,
                               -122.2374743598945],
                    'position': [3.547724739780107,
                                 -43.06645328557224,
                                 -10.56578146599885]},
            'settings': {'color': (0.0,
                                   0.3239000141620636,
                                   5.6280999183654785),
                         'emitDiffuse': True,
                         'emitSpecular': False,
                         'intensity': 0.3012048304080963},
            'type': 'directionalLight'},
 'fill': {'dag': {'orient': [6.021293815996969,
                             -47.2498799893876,
                             -157.544471164769],
                  'position': [-22.95220090618728,
                               17.721858359803672,
                               -29.056418477278378]},
          'settings': {'color': (0.13599999248981476,
                                 0.42320001125335693,
                                 4.389999866485596),
                       'emitDiffuse': True,
                       'emitSpecular': False,
                       'intensity': 0.12048192322254181},
          'type': 'directionalLight'},
 'key': {'dag': {'orient': [42.62638231222449,
                            -50.02563229135204,
                            -121.6387437958025],
                 'position': [-9.275575559796462,
                              17.437620897146054,
                              40.0118297452949]},
         'settings': {'color': (0.10019999742507935,
                                0.3540000021457672,
                                2.2353999614715576),
                      'emitDiffuse': True,
                      'emitSpecular': False,
                      'intensity': 1.2048193216323853},
         'type': 'directionalLight'},
 'moon': {'dag': {'orient': [-113.03934892522275,
                             -25.422554284168264,
                             24.674087488835898],
                  'position': [39.7792405223839,
                               19.6362402847432,
                               -3.3123372951777093]},
          'settings': {'color': (0.5881999731063843,
                                 0.8781999945640564,
                                 1.0),
                       'emitDiffuse': True,
                       'emitSpecular': True,
                       'intensity': 1.5060241222381592},
          'type': 'directionalLight'}},

'dusk':{'bounce': {'dag': {'orient': [87.94325143524775,
                               116.68751423995363,
                               -0.06945976091006908],
                    'position': [0.7756214807648631,
                                 -43.90702197198908,
                                 -7.107272351944391]},
            'settings': {'color': (0.7497999668121338,
                                   0.4666999578475952,
                                   0.5026999711990356),
                         'emitDiffuse': True,
                         'emitSpecular': False,
                         'intensity': 0.5099999904632568},
            'type': 'directionalLight'},
 'fill': {'dag': {'orient': [-12.511525793064292,
                             -37.325301493616834,
                             -143.79526596844832],
                  'position': [-29.452097744940573,
                               15.603704605532231,
                               -23.9633383712581]},
          'settings': {'color': (0.5640000104904175,
                                 0.2955999970436096,
                                 1.059999942779541),
                       'emitDiffuse': True,
                       'emitSpecular': False,
                       'intensity': 1.0199999809265137},
          'type': 'directionalLight'},
 'key': {'dag': {'orient': [79.25328190180231,
                            -45.29057839615513,
                            -119.8858653376537],
                 'position': [0.9913228695992666,
                              21.140445331812693,
                              39.282977155829116]},
         'settings': {'color': (1.0, 0.632269024848938, 0.5449999570846558),
                      'emitDiffuse': True,
                      'emitSpecular': False,
                      'intensity': 1.5437037944793701},
         'type': 'directionalLight'},
 'sun': {'dag': {'orient': [-2.765755479863683,
                            215.48437959224887,
                            2.706486368838884],
                 'position': [37.71506084826539,
                              18.3209047168682,
                              -14.861363429441528]},
         'settings': {'color': (0.9692000150680542,
                                0.017100000753998756,
                                0.0),
                      'emitDiffuse': True,
                      'emitSpecular': True,
                      'intensity': 2.9100000858306885},
         'type': 'directionalLight'}},


'day':{'back': {'dag': {'orient': [156.88025647267793,
                             -58.82863613417641,
                             -161.03441868178112],
                  'position': [-27.35515542400547,
                               18.183013006432834,
                               -24.62146938397566]},
          'settings': {'color': (0.030300000682473183,
                                 0.746399998664856,
                                 0.9336000084877014),
                       'emitDiffuse': True,
                       'emitSpecular': False,
                       'intensity': 0.1807228922843933},
          'type': 'directionalLight'},
 'bounce': {'dag': {'orient': [-52.99849590421887,
                               64.70275249747276,
                               -147.38360533170749],
                    'position': [1.92391331019174,
                                 -42.81523971208047,
                                 -11.920373038912135]},
            'settings': {'color': (0.53329998254776,
                                   3.1953999996185303,
                                   8.616399765014648),
                         'emitDiffuse': True,
                         'emitSpecular': False,
                         'intensity': 0.12048192322254181},
            'type': 'directionalLight'},
 'fill': {'dag': {'orient': [-6.8520975140597375,
                             -31.43758394398881,
                             -47.81295999117311],
                  'position': [-27.35515542400547,
                               18.183013006432834,
                               -24.62146938397566]},
          'settings': {'color': (0.8756999969482422, 0.949999988079071, 1.0),
                       'emitDiffuse': True,
                       'emitSpecular': False,
                       'intensity': 0.4819277226924896},
          'type': 'directionalLight'},
 'key': {'dag': {'orient': [-69.8824329876428,
                            -1.2533274257999782,
                            -90.32101870024927],
                 'position': [-2.795426832051088,
                              16.54558868551412,
                              41.345888888267716]},
         'settings': {'color': (0.29409998655319214,
                                0.9491000175476074,
                                1.0),
                      'emitDiffuse': True,
                      'emitSpecular': False,
                      'intensity': 0.5421686768531799},
         'type': 'directionalLight'},
 'sun': {'dag': {'orient': [49.576861790364674,
                            -55.29176340653097,
                            -143.61076250638163],
                 'position': [38.6836828754513,
                              19.941031093515342,
                              -9.212461426450421]},
         'settings': {'color': (1.0, 1.0, 0.7840999960899353),
                      'emitDiffuse': True,
                      'emitSpecular': True,
                      'intensity': 1.4457831382751465},
         'type': 'directionalLight'}},
              
'dawn':{'bounce': {'dag': {'orient': [-144.63540513531757,
                               56.07623520180962,
                               133.15725988333307],
                    'position': [1.551657329993652,
                                 -43.05996826116251,
                                 -11.062232156885129]},
            'settings': {'color': (0.6014000177383423,
                                   0.9336000084877014,
                                   0.642799973487854),
                         'emitDiffuse': True,
                         'emitSpecular': False,
                         'intensity': 0.2409638613462448},
            'type': 'directionalLight'},
 'fill': {'dag': {'orient': [71.69650392069487,
                             20.109339950326394,
                             -105.57172903977651],
                  'position': [-27.615202279784253,
                               17.811324977369097,
                               -24.602856551360013]},
          'settings': {'color': (0.3310999870300293,
                                 1.0428999662399292,
                                 1.0599000453948975),
                       'emitDiffuse': True,
                       'emitSpecular': False,
                       'intensity': 0.4819277226924896},
          'type': 'directionalLight'},
 'key': {'dag': {'orient': [-32.84413260542846,
                            -1.905577525824222,
                            -66.00048581323438],
                 'position': [-2.1301429462259667,
                              17.404380369112385,
                              41.03173746114638]},
         'settings': {'color': (1.0, 0.8953999876976013, 0.460999995470047),
                      'emitDiffuse': True,
                      'emitSpecular': False,
                      'intensity': 0.5421686768531799},
         'type': 'directionalLight'},
 'sun': {'dag': {'orient': [-26.91396212851115,
                            83.78002141838385,
                            -20.205613317367337],
                 'position': [38.64317940264262,
                              19.55294609427885,
                              -10.165061342867975]},
         'settings': {'color': (0.9692000150680542,
                                0.7670999765396118,
                                0.628600001335144),
                      'emitDiffuse': True,
                      'emitSpecular': True,
                      'intensity': 1.626505970954895},
         'type': 'directionalLight'}},
              
'modeling2':{'backRight': {'dag': {'orient': [136.17568125991207,
                                  -5.403557221141423,
                                  92.31703659886364],
                       'position': [0.0, 0.0, 0.0]},
               'settings': {'color': (1.100000023841858,
                                      0.4307999908924103,
                                      0.0),
                            'emitDiffuse': True,
                            'emitSpecular': False,
                            'intensity': 2.1686747074127197},
               'type': 'directionalLight'},
 'back_left': {'dag': {'orient': [135.44496459052417,
                                  23.92850889050702,
                                  -82.07109919854948],
                       'position': [0.0, 0.0, 0.0]},
               'settings': {'color': (0.0,
                                      1.8055000305175781,
                                      6.924900054931641),
                            'emitDiffuse': True,
                            'emitSpecular': False,
                            'intensity': 1.0137349367141724},
               'type': 'directionalLight'},
 'bottom': {'dag': {'orient': [34.53120806729824,
                               62.47991491562158,
                               -64.27489905221077],
                    'position': [0.0, 0.0, 0.0]},
            'settings': {'color': (1.409999966621399,
                                   0.6762666702270508,
                                   1.2300000190734863),
                         'emitDiffuse': True,
                         'emitSpecular': False,
                         'intensity': 0.24289163947105408},
            'type': 'directionalLight'},
 'key': {'dag': {'orient': [-18.06804200516728,
                            -42.404848414220375,
                            -74.11135559616103],
                 'position': [0.0, 0.0, 0.0]},
         'settings': {'color': (0.8999999761581421,
                                0.8999999761581421,
                                0.8999999761581421),
                      'emitDiffuse': True,
                      'emitSpecular': True,
                      'intensity': 1.399999976158142},
         'type': 'directionalLight'}},
              'modeling3':{'back': {'dag': {'orient': [-125.77524506677436,
                             8.347162363904486,
                             -5.668763199683938],
                  'position': [4.045930614207467,
                               19.175796558228864,
                               -15.361339970973363]},
          'settings': {'color': (1.0,
                                 0.8830000162124634,
                                 0.5550000071525574),
                       'emitDiffuse': True,
                       'emitSpecular': False,
                       'intensity': 2.349397659301758},
          'type': 'directionalLight'},
 'backLeft': {'dag': {'orient': [-214.76729484580866,
                                 -14.82573665302876,
                                 65.03813994071737],
                      'position': [-27.514374322871124,
                                   11.969284970091266,
                                   -28.014972208005677]},
              'settings': {'color': (0.0, 0.559499979019165, 7.0),
                           'emitDiffuse': True,
                           'emitSpecular': False,
                           'intensity': 3.9759035110473633},
              'type': 'directionalLight'},
 'backRight': {'dag': {'orient': [229.02632507642636,
                                  13.10260306294684,
                                  78.43251021979783],
                       'position': [39.08846150582526,
                                    14.608376902770981,
                                    -15.415219388288676]},
               'settings': {'color': (1.100000023841858,
                                      0.7000000476837158,
                                      0.0),
                            'emitDiffuse': True,
                            'emitSpecular': False,
                            'intensity': 1.8674699068069458},
               'type': 'directionalLight'},
 'bottom': {'dag': {'orient': [18.37119693339291,
                               29.779987012140708,
                               -56.36517089723409],
                    'position': [0.9774718697919795,
                                 13.92863643706667,
                                 0.7813131405012962]},
            'settings': {'color': (0.6014000177383423,
                                   0.6014999747276306,
                                   1.0),
                         'emitDiffuse': True,
                         'emitSpecular': False,
                         'intensity': 0.4819277226924896},
            'type': 'directionalLight'},
 'key': {'dag': {'orient': [-27.207392095371375,
                            -53.04927512305759,
                            -75.03334494188157],
                 'position': [-0.5039736050958833,
                              27.5188165720406,
                              35.12142065982375]},
         'settings': {'color': (1.0, 1.0, 1.0),
                      'emitDiffuse': True,
                      'emitSpecular': True,
                      'intensity': 1.2650601863861084},
         'type': 'directionalLight'}},
              
              'stage1':{'backRight': {'dag': {'orient': [148.54186682638465,
                                  -22.547444378937172,
                                  60.29922179873509],
                       'position': [0.0, 0.0, 0.0]},
               'settings': {'color': (1.0276000499725342,
                                      0.0,
                                      1.100000023841858),
                            'emitDiffuse': True,
                            'emitSpecular': False,
                            'intensity': 4.57831335067749},
               'type': 'directionalLight'},
 'back_left': {'dag': {'orient': [181.63596909332227,
                                  37.71213762468457,
                                  -23.007316742132033],
                       'position': [0.0, 0.0, 0.0]},
               'settings': {'color': (0.0,
                                      6.022799968719482,
                                      6.924900054931641),
                            'emitDiffuse': True,
                            'emitSpecular': False,
                            'intensity': 0.5421686768531799},
               'type': 'directionalLight'},
 'bottom': {'dag': {'orient': [-142.98955792303607,
                               54.04673810541476,
                               108.39492975367044],
                    'position': [0.0, 0.0, 0.0]},
            'settings': {'color': (0.8039000034332275, 1.0, 1.0),
                         'emitDiffuse': True,
                         'emitSpecular': False,
                         'intensity': 0.3614457845687866},
            'type': 'directionalLight'},
 'key': {'dag': {'orient': [-8.30336698054406,
                            -22.214403952466515,
                            -94.24783419302064],
                 'position': [0.0, 0.0, 0.0]},
         'settings': {'color': (0.9052000045776367, 0.5490000247955322, 1.0),
                      'emitDiffuse': True,
                      'emitSpecular': True,
                      'intensity': 0.1807228922843933},
         'type': 'directionalLight'},
 'stage': {'dag': {'orient': [-3.7475089260685412,
                              -18.64022631350343,
                              -89.83816593978146],
                   'position': [11.255008469965228,
                                132.58224783781907,
                                158.03258936273755]},
           'settings': {'color': (1.0,
                                  0.9866999983787537,
                                  0.8953999876976013),
                        'coneAngle': 20.60682756780348,
                        'decayRate': 0,
                        'dropoff': 0.0,
                        'emitDiffuse': True,
                        'emitSpecular': True,
                        'intensity': 1.4457831382751465,
                        'penumbraAngle': -10.0},
           'type': 'spotLight'}}}

d_lightCalls = {'directionalLight':mc.directionalLight,
                'pointLight':mc.pointLight,
                'ambientLight':mc.ambientLight,
                'spotLight':mc.spotLight}


def uiMenu(parent):
    _str_func = 'uiMenu'
    
    _uiRoot = mc.menuItem(parent = parent, l='LightLoom Lite', subMenu=True,tearOff=True)
    
    _keys = d_profiles.keys()
    _keys.sort()
    
    mUI.MelMenuItemDiv(_uiRoot,label='Setup')
    
    _uiToPersp = mc.menuItem(parent = _uiRoot,subMenu=True,
                             l='toPersp',
                             )

    _uiToSelected = mc.menuItem(parent = _uiRoot,subMenu=True,
                             l='toSelected',
                             )
    _uiToNone = mc.menuItem(parent = _uiRoot,subMenu=True,
                            l='toWorld',
                            )    
    for k in _keys:
        mc.menuItem(parent = _uiToPersp,
                    l=k,
                    ann = "Setup {0} Orient to persp cam".format(k),
                    c=cgmGEN.Callback(factory, **{'profile':k,'constrainTo':'persp'}))
        mc.menuItem(parent = _uiToSelected,
                    l=k,
                    ann = "Setup {0} Orient to selected".format(k),
                    c=cgmGEN.Callback(factory, **{'profile':k,'constrainTo':'selected'}))        
        mc.menuItem(parent = _uiToNone,
                    l=k,
                    ann = "Setup {0} to world".format(k),
                    c=cgmGEN.Callback(factory, **{'profile':k,'constrainTo':None}))
        
    mUI.MelMenuItemDiv(_uiRoot,label='Utilities')
    mc.menuItem(parent = _uiRoot,
                l='Get Light Dict',
                ann = "Get light dict of selected lights",
                c=cgmGEN.Callback(get_lightDict))    
    mc.menuItem(parent = _uiRoot,
                l='Clean cgmLights',
                ann = "Remove cgmLights from scene",
                c=cgmGEN.Callback(clean_lights))    
    

def get_lightDict(lights=None):
    if lights is None:
        lights = mc.ls(sl=1)
        if not lights:
            log.warning("No lights found")
            return False
        
    _res = {}
    for l in lights:
        mDag = cgmMeta.asMeta(l)
        mLight = mDag.getShapes(asMeta=1)[0]
        _base = str(mDag.p_nameBase)
        if '_cgmLight' in _base:
            _base = _base.replace('_cgmLight','')
        _res[_base] = {}
        d = _res[_base]
        d['type'] = str(mLight.getMayaType())
        d['settings'] = {'intensity':mLight.intensity,
                         'color':mLight.color,
                         'emitSpecular':mLight.emitSpecular,
                         'emitDiffuse':mLight.emitDiffuse,
                         }
        if d['type'] == 'spotLight':
            d['settings']['decayRate'] = mLight.decayRate
            d['settings']['coneAngle'] = mLight.coneAngle
            d['settings']['dropoff'] = mLight.dropoff
            d['settings']['penumbraAngle'] = mLight.penumbraAngle
            
            
        d['dag']= {'position':mDag.p_position,
                   'orient':mDag.p_orient}
        
    pprint.pprint(_res)
    return _res

@cgmGEN.Timer
def clean_lights():
    _str_func = 'clean_lights'
    l_lights = []
    for t in d_lightCalls.keys():
        l_lights.extend(mc.ls(type=t))
    if l_lights:
        log.debug("|{0}| >> existing Lights:  {1} | ...".format(_str_func,len(l_lights)))
        for l in l_lights:
            mLight = cgmMeta.asMeta(l)
            if mLight.getMayaAttr('cgmType') == 'cgmLight':
                log.debug("|{0}| >> cgmLight:  {1} | ...".format(_str_func,mLight))                
                mLight.getTransform(asMeta=1).delete()
    else:
        log.debug("|{0}| >> no existing lights...".format(_str_func)) 
        
    if mc.objExists('cgmLightGroup'):
        mc.delete('cgmLightGroup')        

class factory(object):
    @cgmGEN.Timer
    def __init__(self, profile = 'default', constrainMode = 'orient', constrainTo = 'selected', clean = True, forceNew = True, autoBuild = True, *a,**kws):
        """
        Simple light studio setup idea

        """
        _str_func = 'factory._init_'
        self.mLightGroup = None
        self.b_clean = clean
        self.profile = profile
        self.constrainTo = None
        
        if a:log.debug("|{0}| >> a: {1}".format(_str_func,a))
        if kws:#...intial population
            self.call_kws = kws
            log.debug("|{0}| >> kws: {1}".format(_str_func,kws))
            
        _sel = mc.ls(sl=1) or False
        
        if constrainTo == 'selected':
            if _sel:
                self.constrainTo = _sel[0]
        else:
            self.constrainTo = constrainTo
        
        if autoBuild:
            clean_lights()
            self.get_lights()
            mLightGroup = cgmMeta.cgmObject(name='cgmLightGroup')
            for mLight in self.ml_lightDags:
                mLight.p_parent = mLightGroup
                
            if self.constrainTo and constrainMode:
                mConstrainTo = cgmMeta.cgmObject(cgmMeta.getTransform(self.constrainTo))
                mLoc = mConstrainTo.doLoc()
                mConstrainTo.resetAttrs(['translate','rotate'])

                mc.orientConstraint(mConstrainTo.mNode,mLightGroup.mNode)
                mConstrainTo.doSnapTo(mLoc)
                mLoc.delete()
                
        if _sel:
            mc.select(_sel)

    @cgmGEN.Timer
    def get_lights(self):
        _str_func = 'factory.get_lights'
        _profile = d_profiles.get(self.profile)
        self.ml_lights = []
        self.ml_lightDags = []

        for n,d in _profile.iteritems():
            _type = d.get('type')
            try:_light = d_lightCalls[_type]()  
            except:
                log.error("|{0}| >> Light create fail {1} | {2}".format(_str_func,n,_type))
                continue
            mLight = cgmMeta.asMeta(_light)
            mLight.addAttr('cgmType','cgmLight',lock=True)
            mDag = mLight.getTransform(asMeta=True)
            mDag.rename("{0}_cgmLight".format(n))
            
            for a,v in d['settings'].iteritems():
                log.debug("|{0}| >> setting {1} | {2}:{3}".format(_str_func,n,a,v))                
                ATTR.set(mLight.mNode,a,v)
                
            mDag.p_position = d['dag']['position']
            mDag.p_orient = d['dag']['orient']
            log.debug("|{0}| >> setting {1} | position:{2}".format(_str_func,n,d['dag']['position']))                
            log.debug("|{0}| >> setting {1} | orient:{2}".format(_str_func,n,d['dag']['orient']))                
                
            self.ml_lightDags.append(mDag)
            self.ml_lights.append(mLight)
            #mDag.doConnectOut('instObjGroups[0]','defaultLightSet.dagSetMembers[0]')
            #mc.sets('defaultLightSet',addElement = mDag.mNode)
            
            
            
class cgmLightMaster(object):
    def __init__(self,node=None,name=None,lightType=None):
        pass
            
            
class cgmLight(cgmMeta.cgmObject): 
    def __init__(self,node=None,name=None,nodeType=None, **kws):
        #>>> TO USE Cached instance ---------------------------------------------------------
        _str_func = 'cgmLight.__init__'        
        if node is None:
            if nodeType not in d_lightCalls.keys():
                raise ValueError,"Unknown light node: {0}".format(nodeType)
            if name is None:
                name = nodeType
            _light = d_lightCalls.get(nodeType)(name=name)
            _dag = cgmMeta.getTransform(_light)
            ATTR.add(_dag,'mClass','string',value='cgmLight',lock=True)
            self.__justCreatedState__ = True                
            node = _dag
                
        try: super(cgmLight, self).__init__(node,name, **kws)
        except StandardError,error:
            raise StandardError, "cgmLight.__init__ fail! | %s"%error
        
        for a in ['mShape']:
            if a not in self.UNMANAGED:
                self.UNMANAGED.append(a)
                
        self.mShape = None

        if self.cached:
            log.debug("|{0}| >> cached | {1}".format(_str_func,self.cached))
            return
        
        self.mShape = self.getShapes(asMeta=1)[0]
        
        
    def __createnodeasdf__(self, nodeType, name):
        '''
        :param nodeType: type of node to create
        :param name: name of the new node
        '''
        _str_func = 'cgmLight.__createnode__'        
        
        #Trying to use the light shape as the metaClass caused all sorts of issues. Best just to use the dag
        _light = d_lightCalls.get(nodeType)(name=name)
        _dag = cgmMeta.getTransform(_light)
        ATTR.add(_dag,'mClass','string',value='cgmLight')
        self.__justCreatedState__ = True
        return _dag, True
    
    def __getattribute3__(self, attr):
        '''
        Overload the method to always return the MayaNode
        attribute if it's been serialized to the MayaNode
        '''
        err = None
        try:
            _str_func = 'cgmLight.__getattribute__'            
            log.debug("|{0}| >> trying dag | {1}".format(_str_func,attr))            
            return r9Meta.MetaClass.__getattribute__(self,attr)
        except Exception,err:
            try:
                log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
                return r9Meta.MetaClass.__getattribute__(self.mShape,attr)
            except Exception,err:
                pass
        #finally:
        #    log.debug("|{0}| >> err: {1}".format(_str_func,err))
        #    return

    def __setattr2__(self, attr, value, force=True, **kws):
        err = None
        if not ATTR.has_attr(self.mNode, attr):
            log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
            try:
                if ATTR.has_attr(self.mShape.mNode,attr):
                    log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
                    return r9Meta.MetaClass.__getattribute__(self.mShape,attr, value, force=True, **kws)
            except Exception,err:
                log.debug("|{0}| >> shape attempt err: {1}".format(_str_func,err))
        return r9Meta.MetaClass.__setattr__(self,attr, value, force=True, **kws)
        
        
        try:
            _str_func = 'cgmLight.__setattr__'            
            log.debug("|{0}| >> trying dag | {1}".format(_str_func,attr))
            
            r9Meta.MetaClass.__setattr__(self,attr, value, force=True, **kws)
        except Exception,err:
            try:
                log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
                r9Meta.MetaClass.__getattribute__(self.mShape,attr, value, force=True, **kws)
            except Exception,err:
                pass
        #finally:
        #    log.debug("|{0}| >> err: {1}".format(_str_func,err))
        #    return
    
class cgmLightShape(cgmMeta.cgmNode): 
    def __init__(self,node=None,name=None,nodeType=None, **kws):
        #>>> TO USE Cached instance ---------------------------------------------------------
        _str_func = 'cgmLight.__init__'        
        if node is None:
            if nodeType not in d_lightCalls.keys():
                raise ValueError,"Unknown light node: {0}".format(nodeType)
            if name is None:
                name = nodeType
            _light = d_lightCalls.get(nodeType)(name=name)
            _dag = cgmMeta.getTransform(_light)
            ATTR.add(_dag,'mClass','string',value='cgmLight',lock=True)
            self.__justCreatedState__ = True                
            node = _dag
                
        try: super(cgmLight, self).__init__(node,name, **kws)
        except StandardError,error:
            raise StandardError, "cgmLight.__init__ fail! | %s"%error
        
        for a in ['mShape']:
            if a not in self.UNMANAGED:
                self.UNMANAGED.append(a)
                
        self.mShape = None

        if self.cached:
            log.debug("|{0}| >> cached | {1}".format(_str_func,self.cached))
            return
        
        self.mShape = self.getShapes(asMeta=1)[0]
        
        
    def __createnodeasdf__(self, nodeType, name):
        '''
        :param nodeType: type of node to create
        :param name: name of the new node
        '''
        _str_func = 'cgmLight.__createnode__'        
        
        #Trying to use the light shape as the metaClass caused all sorts of issues. Best just to use the dag
        _light = d_lightCalls.get(nodeType)(name=name)
        _dag = cgmMeta.getTransform(_light)
        ATTR.add(_dag,'mClass','string',value='cgmLight')
        self.__justCreatedState__ = True
        return _dag, True
    
    def __getattribute3__(self, attr):
        '''
        Overload the method to always return the MayaNode
        attribute if it's been serialized to the MayaNode
        '''
        err = None
        try:
            _str_func = 'cgmLight.__getattribute__'            
            log.debug("|{0}| >> trying dag | {1}".format(_str_func,attr))            
            return r9Meta.MetaClass.__getattribute__(self,attr)
        except Exception,err:
            try:
                log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
                return r9Meta.MetaClass.__getattribute__(self.mShape,attr)
            except Exception,err:
                pass
        #finally:
        #    log.debug("|{0}| >> err: {1}".format(_str_func,err))
        #    return

    def __setattr2__(self, attr, value, force=True, **kws):
        err = None
        if not ATTR.has_attr(self.mNode, attr):
            log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
            try:
                if ATTR.has_attr(self.mShape.mNode,attr):
                    log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
                    return r9Meta.MetaClass.__getattribute__(self.mShape,attr, value, force=True, **kws)
            except Exception,err:
                log.debug("|{0}| >> shape attempt err: {1}".format(_str_func,err))
        return r9Meta.MetaClass.__setattr__(self,attr, value, force=True, **kws)
        
        
        try:
            _str_func = 'cgmLight.__setattr__'            
            log.debug("|{0}| >> trying dag | {1}".format(_str_func,attr))
            
            r9Meta.MetaClass.__setattr__(self,attr, value, force=True, **kws)
        except Exception,err:
            try:
                log.debug("|{0}| >> trying shape | {1}".format(_str_func,attr))                            
                r9Meta.MetaClass.__getattribute__(self.mShape,attr, value, force=True, **kws)
            except Exception,err:
                pass
        #finally:
        #    log.debug("|{0}| >> err: {1}".format(_str_func,err))
        #    return
        
        
#=========================================================================      
# R9 Stuff - We force the update on the Red9 internal registry  
#=========================================================================    
r9Meta.registerMClassInheritanceMapping()#Pushes our classes in
