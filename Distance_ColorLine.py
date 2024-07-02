# -*- coding: utf-8 -*-
import sys

import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.api.OpenMayaRender as OpenMayaRender

def maya_useNewAPI():
    pass

#=========================================
class Distance_ColorLine( OpenMayaUI.MPxLocatorNode ):
    
    # ノードのアトリビュート名
    kPluginNodeTypeName = "Distance_ColorLine"
    
    #TypeIDを入れる
    NodeId = OpenMaya.MTypeId(0x80011)#ユニークID
    
    #オーバーライド用のID
    classfication = 'drawdb/geometry/Distance_ColorLine'
    registrantId = 'Distance_ColorLinePlugin'
    
    #-----------------------------------------------
    def __init__(self):
        OpenMayaUI.MPxLocatorNode.__init__(self)
    
    #-----------------------------------------------
    def draw( self, view, path, style, status ):
        pass
    
    #-----------------------------------------------
    def isBounded( self ):
        return True
    
    #-----------------------------------------------
    def boundingBox( self ):
    
        return OpenMaya.MBoundingBox( OpenMaya.MPoint( 1.0, 1.0, 1.0 ), 
        OpenMaya.MPoint( -1.0, -1.0, -1.0 ) )
    
    #-----------------------------------------------
    # creator
    @staticmethod
    def nodeCreator():
        return Distance_ColorLine()
    
    #-----------------------------------------------
    # initializer
    @staticmethod
    def nodeInitializer():
    
        # アトリビュートの種類の定義
        fnCompAttr = OpenMaya.MFnCompoundAttribute()
        fnMessageAttr = OpenMaya.MFnMessageAttribute()
        typedAttr = OpenMaya.MFnTypedAttribute()
        fnNumericAttr = OpenMaya.MFnNumericAttribute()

        # 描画を実行するチェックのブールアトリビュート
        Distance_ColorLine.abool = fnNumericAttr.create( 'bool', 'bl', OpenMaya.MFnNumericData.kBoolean)
        fnNumericAttr.writable = True
        fnNumericAttr.keyable = True
        
        # ベースメッシュ用のアトリビュート
        typedAttr = OpenMaya.MFnTypedAttribute()
        Distance_ColorLine.baseinput = typedAttr.create('baseinput', 'baseinputMesh', OpenMaya.MFnData.kMesh)
        typedAttr.writable = True
        typedAttr.keyable = True
        
        # ターゲットメッシュ用のアトリビュート
        Distance_ColorLine.input = typedAttr.create('input', 'inputMesh', OpenMaya.MFnData.kMesh)
        typedAttr.writable = True
        typedAttr.keyable = True


        # カラー描画の変化距離を設定するアトリビュート
        Distance_ColorLine.distance = fnNumericAttr.create( 'distance', 'dis', OpenMaya.MFnNumericData.kFloat,2.0)
        fnNumericAttr.writable = True
        fnNumericAttr.keyable = True
        
        # アトリビュートをセットする
        Distance_ColorLine.addAttribute( Distance_ColorLine.abool ) 
        Distance_ColorLine.addAttribute( Distance_ColorLine.baseinput )
        Distance_ColorLine.addAttribute( Distance_ColorLine.input )
        Distance_ColorLine.addAttribute( Distance_ColorLine.distance )
        
        return True
        
        
#=========================================
class UserData( OpenMaya.MUserData ):

    #Distance_ColorLineに渡すデータ
    size = 0.0
    #-----------------------------------------------
    def __init__( self ):
        OpenMaya.MUserData.__init__( self, False )
        self.datas = []
        self.basedatas = []
        self.distance = 0.0
#=========================================
class DrawOverrideOverride( OpenMayaRender.MPxDrawOverride ):
    
    #-----------------------------------------------
    def __init__( self, obj ):
        OpenMayaRender.MPxDrawOverride.__init__( self, obj, DrawOverrideOverride.draw )
    
    #-----------------------------------------------
    @staticmethod
    def draw( context, data ):
        pass
    
    #-----------------------------------------------
    def supportedDrawAPIs( self ):

        #描画する
        return OpenMayaRender.MRenderer.kAllDevices
    #-----------------------------------------------
    def hasUIDrawables( self ):
        return True
    
    #-----------------------------------------------
    def isBounded( self, objPath, cameraPath ):
        return True
    
    #-----------------------------------------------
    def boundingBox( self, objPath, cameraPath ):
    
        boxsize = 10000.0
        bbox = OpenMaya.MBoundingBox(OpenMaya.MPoint(boxsize, boxsize, boxsize),
        OpenMaya.MPoint(-boxsize, -boxsize, -boxsize))
    
        return bbox
    #-----------------------------------------------
    def disableInternalBoundingBoxDraw( self ):
        return True
    
    #-----------------------------------------------
    def prepareForDraw( self, objPath, cameraPath, frameContext, oldData ):

        # データ更新処理
        if( objPath ):
            newData = None
            if( oldData ):
                newData = oldData
                newData.datas = []
            else:
                newData = UserData()
            
            # 自身のロケータの情報を読み込む
            thisNode = objPath.node()
            fnNode = OpenMaya.MFnDependencyNode( thisNode )
            fnDagNode = OpenMaya.MFnDagNode( thisNode )
            
            # boolプラグからデータを読み込み、Trueならば実行
            boolPlug = fnNode.findPlug( 'bool', False ).asBool()
            if boolPlug == True:
                meshPlug = fnNode.findPlug( 'input', False ).asMObject()
                oMesh = OpenMaya.MFnMesh(meshPlug)
                
                baseMeshPlug = fnNode.findPlug( 'baseinput', False ).asMObject()
                oBaseMesh = OpenMaya.MFnMesh(baseMeshPlug)

                # ベースのメッシュとターゲットのメッシュの頂点の位置情報を取得してデータ保存
                newData.datas.append(oMesh.getPoints())
                newData.basedatas.append(oBaseMesh.getPoints())

                # カラー描画の変化距離
                distancePlug = fnNode.findPlug( 'distance', False ).asFloat()
                newData.distance = distancePlug
            return newData

        return None
    
    #-----------------------------------------------
    #描画を制御する
    def addUIDrawables( self, objPath, drawManager, frameContext, data ):

        #描画距離の
        distance = data.distance

        # ベースメッシュのデータが空でなければ、描画処理を実行する
        if data.datas != [] and distance != 0.0:
        
            #メッシュデータを取り出す
            mainpos = data.datas[0]
            basepos = data.basedatas[0]
            
            #頂点数分ループ処理をする
            for i in range(len(mainpos)):
                    
                # ベースメッシュからターゲットメッシュの差を出す
                newvec = OpenMaya.MVector(mainpos[i]) - OpenMaya.MVector(basepos[i])

                #距離で色を変える（distanceアトリビュートの影響を受ける
                bulue = newvec.length()/distance 

                # 差が一定数以下ならば描画処理を行わない
                if bulue <= 0.0001:
                    continue
                    
                # ボックスの描画処理   
                drawManager.beginDrawable()
                color = OpenMaya.MColor([bulue,(1.0-bulue),0.0])
                drawManager.setColor( color )
                drawManager.box(OpenMaya.MPoint(mainpos[i][0],
                mainpos[i][1],mainpos[i][2],1),
                OpenMaya.MVector(0.0,1.0,0.0),OpenMaya.MVector(0.0,0.0,1.0),
                0.01,0.01,0.01,True) # ←表示されるボックスのサイズ
                
                # 元頂点から移動頂点への線を描画する
                drawManager.line(mainpos[i],basepos[i])
                
                #描画の記述を終了する
                drawManager.endDrawable()
                
        return True
    
    #-----------------------------------------------
    @staticmethod
    def creator( obj ):
        return DrawOverrideOverride( obj )
    
#-----------------------------------------------
# initialize
def initializePlugin( obj ):
    
    mplugin = OpenMaya.MFnPlugin( obj, "Distance_ColorLine", "3.0", "Any" )
    try:
        #Override
        mplugin.registerNode( Distance_ColorLine.kPluginNodeTypeName, Distance_ColorLine.NodeId, 
        Distance_ColorLine.nodeCreator, Distance_ColorLine.nodeInitializer, OpenMaya.MPxNode.kLocatorNode,
        Distance_ColorLine.classfication )
    
        #Distance_ColorLine
        OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator( Distance_ColorLine.classfication,
        Distance_ColorLine.registrantId,DrawOverrideOverride.creator )
    													  
    except:
        sys.stderr.write( "Failed to register node: %s" % Distance_ColorLine.kPluginNodeTypeName )
        raise
    
#-----------------------------------------------
# uninitialize
def uninitializePlugin( obj ):
    
    mplugin = OpenMaya.MFnPlugin( obj, "Distance_ColorLine", "3.0", "Any" )
    try:
        mplugin.deregisterNode( Distance_ColorLine.NodeId )
        OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator( Distance_ColorLine.classfication,
        Distance_ColorLine.registrantId )
    except:
        sys.stderr.write( "Failed to deregister node: %s" % Distance_ColorLine.kPluginNodeTypeName )
        raise