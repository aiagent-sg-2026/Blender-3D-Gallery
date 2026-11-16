using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityGLTF;

public static class ChibiV2UnityQA {
    public static void Run() {
        try {
            string path = "Assets/ChibiV2/chibi-visitor-v2.glb";
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null) {
                var assets = AssetDatabase.LoadAllAssetsAtPath(path);
                Debug.Log("CHIBI_UNITY_IMPORT_ASSETS=" + string.Join(",",assets.Select(x => x.name+":"+x.GetType().Name)));
                throw new Exception("GLB importer did not produce GameObject");
            }
            var go = UnityEngine.Object.Instantiate(prefab);
            go.name = "GJH_Chibi_Visitor_V2_Unity_Roundtrip";
            var filters=go.GetComponentsInChildren<MeshFilter>(true);
            var skins=go.GetComponentsInChildren<SkinnedMeshRenderer>(true);
            var renders=go.GetComponentsInChildren<Renderer>(true);
            int meshes=filters.Count(x => x.sharedMesh!=null)+skins.Count(x => x.sharedMesh!=null);
            int verts=filters.Where(x => x.sharedMesh!=null).Sum(x => x.sharedMesh.vertexCount)+skins.Where(x => x.sharedMesh!=null).Sum(x => x.sharedMesh.vertexCount);
            int mats=renders.SelectMany(x=>x.sharedMaterials).Where(x=>x!=null).Select(x=>x.name).Distinct().Count();
            Debug.Log("CHIBI_UNITY_IMPORT_PASS meshes="+meshes+" vertices="+verts+" materials="+mats+" roots="+go.transform.childCount);
            if (meshes<20 || verts<1000 || mats<5) throw new Exception("Imported model below expected geometry/material count");
            var exporter = new GLTFSceneExporter(new Transform[] {go.transform}, new ExportContext());
            string output=Path.Combine(Application.dataPath,"../Exports/ChibiV2");
            Directory.CreateDirectory(output);
            exporter.SaveGLB(output,"chibi-visitor-v2-unity-roundtrip");
            string exported=Path.Combine(output,"chibi-visitor-v2-unity-roundtrip.glb");
            if(!File.Exists(exported)||new FileInfo(exported).Length<10000) throw new Exception("UnityGLTF output missing or empty");
            Debug.Log("CHIBI_UNITY_GLB_EXPORT_PASS bytes="+new FileInfo(exported).Length+" file="+exported);
            EditorApplication.Exit(0);
        } catch(Exception e) {
            Debug.LogError("CHIBI_UNITY_QA_FAIL " + e);
            EditorApplication.Exit(1);
        }
    }
}
