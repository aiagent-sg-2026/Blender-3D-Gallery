using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using GLTFast;
using GLTFast.Export;
using GLTFast.Logging;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using RenderPipeline = UnityEngine.Rendering.RenderPipeline;

public static class ChibiBuilder
{
    const string AssetRoot = "Assets/Chibi";
    const string MeshFolder = AssetRoot + "/Meshes";
    const string MaterialFolder = AssetRoot + "/Materials";
    const string PrefabFolder = AssetRoot + "/Prefabs";
    const string PrefabPath = PrefabFolder + "/GJHChibiVisitor.prefab";
    const string ExportPath = "Exports/gjh-chibi-visitor.glb";
    const int PreviewSize = 1024;
    const int StudioRenderSize = PreviewSize * 2;

    static Mesh sphereMesh;
    static Mesh cubeMesh;
    static Mesh helmetMesh;
    static Mesh lensMesh;
    static Mesh detailMesh;
    static Mesh clothMesh;
    static Mesh roundedBoxMesh;
    static Mesh cylinderMesh;
    static Mesh torusMesh;
    static Mesh finMesh;
    static Mesh heartWedgeMesh;

    static Material whiteMaterial;
    static Material darkMaterial;
    static Material glassMaterial;
    static Material purpleMaterial;
    static Material purpleGlowMaterial;
    static Material lavenderMaterial;
    static Material seamMaterial;
    static Material reflectionMaterial;

    [MenuItem("Tools/GJH/Build Chibi Visitor")]
    public static void BuildAndExport()
    {
        try
        {
            EnsureProjectFolders();
            LoadOrCreateAssets();

            var oldRoot = GameObject.Find("GJHChibiVisitor");
            if (oldRoot != null)
                UnityEngine.Object.DestroyImmediate(oldRoot);

            var root = BuildCharacter();
            var prefabSuccess = false;
            PrefabUtility.SaveAsPrefabAsset(root, PrefabPath, out prefabSuccess);
            if (!prefabSuccess)
                throw new InvalidOperationException("Failed to save the character prefab.");

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            ExportGlb(root);
            RenderPreviews(root);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("[ChibiBuilder] Generated the modular character, prefab, GLB, and four previews.");
            if (Application.isBatchMode)
                Debug.Log($"[ChibiBuilder] GLB: {Path.GetFullPath(ExportPath)} ({new FileInfo(ExportPath).Length} bytes).");
        }
        catch (Exception exception)
        {
            Debug.LogException(exception);
            if (Application.isBatchMode)
                EditorApplication.Exit(1);
        }
    }

    public static async void ValidateExport()
    {
        GameObject importedRoot = null;
        GltfImport importer = null;
        try
        {
            var path = Path.GetFullPath(ExportPath);
            if (!File.Exists(path))
                throw new FileNotFoundException("The exported GLB was not found.", path);

            importer = new GltfImport(deferAgent: new UninterruptedDeferAgent());
            var loaded = await importer.Load(new Uri(path).AbsoluteUri);
            if (!loaded)
                throw new InvalidDataException("glTFast could not reload the exported GLB.");

            importedRoot = new GameObject("GLB Reimport Validation");
            var instantiated = await importer.InstantiateMainSceneAsync(importedRoot.transform);
            if (!instantiated)
                throw new InvalidDataException("glTFast could not instantiate the exported GLB scene.");

            var renderers = importedRoot.GetComponentsInChildren<Renderer>(true);
            if (renderers.Length == 0)
                throw new InvalidDataException("The imported GLB contains no renderers.");

            var bounds = renderers[0].bounds;
            for (var i = 1; i < renderers.Length; i++)
                bounds.Encapsulate(renderers[i].bounds);

            long triangles = 0;
            var filters = importedRoot.GetComponentsInChildren<MeshFilter>(true);
            foreach (var filter in filters)
            {
                var mesh = filter.sharedMesh;
                if (mesh == null)
                    continue;
                for (var subMesh = 0; subMesh < mesh.subMeshCount; subMesh++)
                    triangles += (long)mesh.GetIndexCount(subMesh) / 3;
            }

            var visitor = importedRoot.transform.Find("GJHChibiVisitor");
            if (visitor == null) throw new InvalidDataException("The exported root name changed.");
            foreach (var module in new[] { "Head", "Face", "Ears", "Headphones", "Outfit", "Legs", "Hands", "Feet" })
                if (visitor.Find(module) == null)
                    throw new InvalidDataException("Missing exported module: " + module);
            var exportedEyes = visitor.Find("Face/Eyes");
            if (exportedEyes == null || exportedEyes.Find("Happy") == null || exportedEyes.childCount != 1)
                throw new InvalidDataException("The GLB must contain only the Happy expression.");
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
            var prefabEyes = prefab == null ? null : prefab.transform.Find("Face/Eyes");
            if (prefabEyes == null) throw new InvalidDataException("Prefab expression set is missing.");
            foreach (var expression in new[] { "Happy", "Sleep", "Excited", "Heart" })
            {
                var variant = prefabEyes.Find(expression);
                if (variant == null || variant.gameObject.activeSelf != (expression == "Happy"))
                    throw new InvalidDataException("Incorrect prefab expression state: " + expression);
            }
            if (Mathf.Abs(bounds.min.y) > 0.0001f || bounds.size.y < 0.9f || bounds.size.y > 1.15f)
                throw new InvalidDataException("The character must stand on Y=0 and be approximately one meter tall.");
            Debug.Log("[ChibiBuilder] Verified root, eight modules, prefab expressions, Happy-only export, and ground alignment.");
            var bytes = new FileInfo(path).Length;
            Debug.Log($"[ChibiBuilder] Reimported GLB bounds min={FormatVector(bounds.min)} max={FormatVector(bounds.max)} size={FormatVector(bounds.size)}; triangles={triangles}; bytes={bytes}.");
            if (triangles >= 15000)
                throw new InvalidDataException($"Triangle budget exceeded: {triangles} (limit 15000).");
            if (bytes >= 2 * 1024 * 1024)
                throw new InvalidDataException($"GLB size budget exceeded: {bytes} bytes (limit 2097152).");
        }
        catch (Exception exception)
        {
            Debug.LogException(exception);
            if (Application.isBatchMode)
                EditorApplication.Exit(1);
            return;
        }
        finally
        {
            if (importedRoot != null)
                UnityEngine.Object.DestroyImmediate(importedRoot);
            if (importer != null)
                importer.Dispose();
        }

        if (Application.isBatchMode)
            EditorApplication.Exit(0);
    }

    static GameObject BuildCharacter()
    {
        var root = new GameObject("GJHChibiVisitor");
        root.transform.position = Vector3.zero;
        root.transform.rotation = Quaternion.identity;
        root.transform.localScale = Vector3.one;

        // The helmet is 0.48 m high; the complete mascot is approximately 1.04 m.
        // Keep the mix-and-match groups at the root, sharing one gentle head pose.
        var head = CreateGroup("Head", root.transform);
        CreatePart("HelmetShell", head, helmetMesh, whiteMaterial,
            new Vector3(0f, 0.662f, 0f), new Vector3(0.58f, 0.48f, 0.42f));

        var face = CreateGroup("Face", root.transform);
        CreatePart("ScreenBezel", face, lensMesh, darkMaterial,
            new Vector3(0f, 0.652f, 0.169f), new Vector3(0.506f, 0.335f, 0.094f));
        CreatePart("GlossyFaceScreen", face, lensMesh, glassMaterial,
            new Vector3(0f, 0.652f, 0.188f), new Vector3(0.478f, 0.306f, 0.063f));
        var eyes = CreateGroup("Eyes", face);
        eyes.localPosition = new Vector3(0f, 0.653f, 0.228f);
        CreateExpressions(eyes);
        CreateCurve(face, "SoftScreenReflection", new[] {
            new Vector3(-0.18f, 0.744f, 0.221f), new Vector3(-0.15f, 0.772f, 0.221f),
            new Vector3(-0.115f, 0.777f, 0.221f)}, 0.003f, reflectionMaterial);

        var ears = CreateGroup("Ears", root.transform);
        CreateEar(ears, "LeftEarFin", -1f);
        CreateEar(ears, "RightEarFin", 1f);
        var headphones = CreateGroup("Headphones", root.transform);
        CreateHeadphone(headphones, "LeftHeadphone", -1f);
        CreateHeadphone(headphones, "RightHeadphone", 1f);
        foreach (var module in new[] { head, face, ears, headphones })
        {
            var pivot = new Vector3(0f, 0.662f, 0f);
            var tilt = Quaternion.Euler(0f, 0f, -3f);
            module.localPosition = pivot - tilt * pivot;
            module.localRotation = tilt;
        }

        var outfit = CreateGroup("Outfit", root.transform);
        CreatePart("HoodieTorso", outfit, clothMesh, whiteMaterial,
            new Vector3(0f, 0.325f, 0f), new Vector3(0.342f, 0.254f, 0.246f));
        CreatePart("HoodieRibbedHem", outfit, roundedBoxMesh, whiteMaterial,
            new Vector3(0f, 0.215f, 0.002f), new Vector3(0.337f, 0.040f, 0.252f));
        CreatePart("FoldedHood", outfit, clothMesh, purpleMaterial,
            new Vector3(0f, 0.418f, -0.101f), new Vector3(0.29f, 0.142f, 0.152f));
        CreatePart("HoodLining", outfit, lensMesh, lavenderMaterial,
            new Vector3(0f, 0.442f, -0.157f), new Vector3(0.205f, 0.071f, 0.025f),
            Quaternion.Euler(25f, 180f, 0f));
        CreatePart("HoodCollar", outfit, torusMesh, purpleMaterial,
            new Vector3(0f, 0.435f, 0.005f), new Vector3(0.244f, 0.195f, 0.17f),
            Quaternion.Euler(90f, 0f, 0f));
        CreateSleeve(outfit, "LeftSleeve", -1f);
        CreateSleeve(outfit, "RightSleeve", 1f);
        CreateLogo(outfit);
        CreatePart("KangarooPocket", outfit, roundedBoxMesh, whiteMaterial,
            new Vector3(0f, 0.256f, 0.121f), new Vector3(0.194f, 0.065f, 0.025f));
        foreach (var side in new[] { -1f, 1f })
        {
            CreateCurve(outfit, side < 0 ? "PocketOpeningL" : "PocketOpeningR", new[] {
                new Vector3(side * 0.079f, 0.279f, 0.133f),
                new Vector3(side * 0.066f, 0.269f, 0.136f),
                new Vector3(side * 0.060f, 0.253f, 0.136f)}, 0.0023f, seamMaterial);
            CreateCurve(outfit, side < 0 ? "DrawstringL" : "DrawstringR", new[] {
                new Vector3(side * 0.067f, 0.420f, 0.118f),
                new Vector3(side * 0.074f, 0.399f, 0.130f),
                new Vector3(side * 0.071f, 0.385f, 0.131f)}, 0.0031f, lavenderMaterial);
            CreatePart(side < 0 ? "DrawstringTipL" : "DrawstringTipR", outfit, detailMesh, purpleMaterial,
                new Vector3(side * 0.071f, 0.382f, 0.131f), new Vector3(0.010f, 0.016f, 0.010f));
        }

        var legs = CreateGroup("Legs", root.transform);
        var hands = CreateGroup("Hands", root.transform);
        var feet = CreateGroup("Feet", root.transform);
        foreach (var side in new[] { -1f, 1f })
        {
            var name = side < 0 ? "Left" : "Right";
            CreatePart(name + "Leg", legs, roundedBoxMesh, whiteMaterial,
                new Vector3(side * 0.091f, 0.124f, 0f), new Vector3(0.124f, 0.126f, 0.138f));
            CreatePart(name + "LegPatch", legs, roundedBoxMesh, purpleMaterial,
                new Vector3(side * 0.091f, 0.129f, 0.070f), new Vector3(0.047f, 0.045f, 0.010f));
            CreatePart(name + "Shorts", outfit, roundedBoxMesh, darkMaterial,
                new Vector3(side * 0.079f, 0.182f, -0.009f), new Vector3(0.156f, 0.076f, 0.185f));
            CreatePart(name + "ShortsHem", outfit, roundedBoxMesh, purpleMaterial,
                new Vector3(side * 0.079f, 0.153f, -0.009f), new Vector3(0.153f, 0.018f, 0.181f));
            CreatePart(name + "Mitten", hands, sphereMesh, darkMaterial,
                new Vector3(side * 0.248f, 0.252f, 0.014f), new Vector3(0.106f, 0.100f, 0.103f),
                Quaternion.Euler(0f, 0f, side * 12f));
            CreatePart(name + "Thumb", hands, detailMesh, darkMaterial,
                new Vector3(side * 0.217f, 0.261f, 0.051f), new Vector3(0.046f, 0.056f, 0.052f));
            CreatePart(name + "Shoe", feet, sphereMesh, darkMaterial,
                new Vector3(side * 0.099f, 0.045f, 0.033f), new Vector3(0.155f, 0.090f, 0.182f));
            CreatePart(name + "ShoeTab", feet, roundedBoxMesh, purpleMaterial,
                new Vector3(side * 0.099f, 0.056f, -0.057f), new Vector3(0.041f, 0.035f, 0.014f));
        }

        return root;
    }

    static void CreateExpressions(Transform eyes)
    {
        var happy = CreateGroup("Happy", eyes);
        for (var side = -1; side <= 1; side += 2)
        {
            var points = new List<Vector3>();
            for (var i = 0; i <= 14; i++)
            {
                var t = i / 14f;
                points.Add(new Vector3(side * 0.102f + Mathf.Lerp(-0.047f, 0.047f, t),
                    -0.002f + 0.054f * Mathf.Sin(t * Mathf.PI), 0f));
            }
            CreateCurve(happy, side < 0 ? "LeftHappyArc" : "RightHappyArc", points.ToArray(), 0.009f, purpleGlowMaterial);
            CreatePart(side < 0 ? "LeftCheek" : "RightCheek", happy, detailMesh, purpleMaterial,
                new Vector3(side * 0.164f, -0.030f, -0.001f), new Vector3(0.025f, 0.011f, 0.006f));
        }
        var smile = new List<Vector3>();
        for (var i = 0; i <= 10; i++)
        {
            var t = i / 10f;
            smile.Add(new Vector3(Mathf.Lerp(-0.028f, 0.028f, t), -0.049f - 0.013f * Mathf.Sin(t * Mathf.PI), 0f));
        }
        CreateCurve(happy, "TinySmile", smile.ToArray(), 0.0045f, purpleGlowMaterial);
        happy.gameObject.SetActive(true);

        var sleep = CreateGroup("Sleep", eyes);
        CreateStroke(sleep, "LeftSleepEye", new Vector3(-0.105f, 0.018f, 0f), new Vector3(-0.035f, 0.018f, 0f), 0.0055f, purpleGlowMaterial);
        CreateStroke(sleep, "RightSleepEye", new Vector3(0.035f, 0.018f, 0f), new Vector3(0.105f, 0.018f, 0f), 0.0055f, purpleGlowMaterial);
        sleep.gameObject.SetActive(false);

        var excited = CreateGroup("Excited", eyes);
        CreateStroke(excited, "LeftExcitedEyeA", new Vector3(-0.105f, 0.045f, 0f), new Vector3(-0.058f, 0.008f, 0f), 0.0055f, purpleGlowMaterial);
        CreateStroke(excited, "LeftExcitedEyeB", new Vector3(-0.058f, 0.008f, 0f), new Vector3(-0.105f, -0.029f, 0f), 0.0055f, purpleGlowMaterial);
        CreateStroke(excited, "RightExcitedEyeA", new Vector3(0.105f, 0.045f, 0f), new Vector3(0.058f, 0.008f, 0f), 0.0055f, purpleGlowMaterial);
        CreateStroke(excited, "RightExcitedEyeB", new Vector3(0.058f, 0.008f, 0f), new Vector3(0.105f, -0.029f, 0f), 0.0055f, purpleGlowMaterial);
        excited.gameObject.SetActive(false);

        var heart = CreateGroup("Heart", eyes);
        CreateHeart(heart, "LeftHeart", -0.065f);
        CreateHeart(heart, "RightHeart", 0.065f);
        heart.gameObject.SetActive(false);
    }

    static void CreateHeart(Transform parent, string name, float x)
    {
        CreatePart(name + "Point", parent, heartWedgeMesh, purpleGlowMaterial,
            new Vector3(x, 0.012f, 0f), new Vector3(0.034f, 0.041f, 0.009f));
        CreatePart(name + "LeftLobe", parent, sphereMesh, purpleGlowMaterial,
            new Vector3(x - 0.008f, 0.021f, 0.002f), new Vector3(0.022f, 0.022f, 0.01f));
        CreatePart(name + "RightLobe", parent, sphereMesh, purpleGlowMaterial,
            new Vector3(x + 0.008f, 0.021f, 0.002f), new Vector3(0.022f, 0.022f, 0.01f));
    }

    static void CreateEar(Transform parent, string name, float side)
    {
        var ear = CreateGroup(name, parent);
        ear.localPosition = new Vector3(side * 0.218f, 0.800f, -0.014f);
        ear.localRotation = Quaternion.Euler(-13f, side * 8f, side * -12f);
        CreatePart("WhiteFinShell", ear, finMesh, whiteMaterial, Vector3.zero,
            new Vector3(0.100f, 0.245f, 0.062f));
        CreatePart("LavenderInset", ear, finMesh, lavenderMaterial,
            new Vector3(0f, 0.028f, 0.021f), new Vector3(0.060f, 0.183f, 0.029f));
    }

    static void CreateHeadphone(Transform parent, string name, float side)
    {
        var cup = CreateGroup(name, parent);
        cup.localPosition = new Vector3(side * 0.281f, 0.660f, -0.003f);
        cup.localRotation = Quaternion.LookRotation(new Vector3(side, 0f, 0.18f).normalized, Vector3.up);
        CreatePart("EarCushion", cup, sphereMesh, darkMaterial,
            Vector3.zero, new Vector3(0.173f, 0.184f, 0.090f));
        CreatePart("WhiteCupHousing", cup, sphereMesh, whiteMaterial,
            new Vector3(0f, 0f, 0.027f), new Vector3(0.167f, 0.178f, 0.065f));
        CreatePart("BlackOuterDisc", cup, sphereMesh, darkMaterial,
            new Vector3(0f, 0f, 0.051f), new Vector3(0.150f, 0.159f, 0.037f));
        CreatePart("PurpleGlowRing", cup, torusMesh, purpleGlowMaterial,
            new Vector3(0f, 0f, 0.069f), new Vector3(0.112f, 0.112f, 0.075f));
        CreatePart("CenterCap", cup, sphereMesh, glassMaterial,
            new Vector3(0f, 0f, 0.066f), new Vector3(0.074f, 0.074f, 0.015f));
        CreatePart("StatusLED", cup, detailMesh, purpleGlowMaterial,
            new Vector3(0f, 0f, 0.077f), new Vector3(0.014f, 0.014f, 0.008f));
    }

    static void CreateSleeve(Transform outfit, string name, float side)
    {
        var sleeve = CreateGroup(name, outfit);
        sleeve.localPosition = new Vector3(side * 0.199f, 0.344f, -0.010f);
        sleeve.localRotation = Quaternion.Euler(-5f, 0f, side * 23f);
        CreatePart("PuffySleeve", sleeve, clothMesh, whiteMaterial,
            Vector3.zero, new Vector3(0.137f, 0.156f, 0.169f));
        CreatePart("PurplePanel", sleeve, roundedBoxMesh, purpleMaterial,
            new Vector3(side * 0.021f, 0.006f, 0.083f), new Vector3(0.052f, 0.102f, 0.017f));
        CreatePart("RibbedCuff", sleeve, roundedBoxMesh, lavenderMaterial,
            new Vector3(0f, -0.064f, 0f), new Vector3(0.116f, 0.033f, 0.148f));
    }

    static void CreateLogo(Transform outfit)
    {
        var z = 0.108f;
        var r = 0.0038f;
        CreateLogoStroke(outfit, "GJH_G_Top", new Vector3(-0.061f, 0.53f, z), new Vector3(-0.027f, 0.53f, z), r);
        CreateLogoStroke(outfit, "GJH_G_Left", new Vector3(-0.061f, 0.53f, z), new Vector3(-0.061f, 0.482f, z), r);
        CreateLogoStroke(outfit, "GJH_G_Bottom", new Vector3(-0.061f, 0.482f, z), new Vector3(-0.027f, 0.482f, z), r);
        CreateLogoStroke(outfit, "GJH_G_Right", new Vector3(-0.027f, 0.482f, z), new Vector3(-0.027f, 0.505f, z), r);
        CreateLogoStroke(outfit, "GJH_G_Middle", new Vector3(-0.027f, 0.505f, z), new Vector3(-0.047f, 0.505f, z), r);

        CreateLogoStroke(outfit, "GJH_J_Top", new Vector3(-0.008f, 0.53f, z), new Vector3(0.026f, 0.53f, z), r);
        CreateLogoStroke(outfit, "GJH_J_Right", new Vector3(0.026f, 0.53f, z), new Vector3(0.026f, 0.491f, z), r);
        CreateLogoStroke(outfit, "GJH_J_Bottom", new Vector3(0.026f, 0.491f, z), new Vector3(0.009f, 0.482f, z), r);
        CreateLogoStroke(outfit, "GJH_J_Left", new Vector3(0.009f, 0.482f, z), new Vector3(0.002f, 0.49f, z), r);

        CreateLogoStroke(outfit, "GJH_H_Left", new Vector3(0.043f, 0.482f, z), new Vector3(0.043f, 0.53f, z), r);
        CreateLogoStroke(outfit, "GJH_H_Middle", new Vector3(0.043f, 0.506f, z), new Vector3(0.077f, 0.506f, z), r);
        CreateLogoStroke(outfit, "GJH_H_Right", new Vector3(0.077f, 0.482f, z), new Vector3(0.077f, 0.53f, z), r);
    }

    static void CreateLogoStroke(Transform parent, string name, Vector3 start, Vector3 end, float radius)
    {
        // Mirror the lettering to read GJH when viewed from the character's +Z front.
        start = new Vector3(-(start.x - 0.008f) * 1.48f, (start.y - 0.506f) * 1.18f + 0.344f, 0.128f);
        end = new Vector3(-(end.x - 0.008f) * 1.48f, (end.y - 0.506f) * 1.18f + 0.344f, 0.128f);
        radius *= 1.35f;
        CreateStroke(parent, name, start, end, radius, purpleMaterial);
    }

    static void CreateStroke(Transform parent, string name, Vector3 start, Vector3 end, float radius, Material material)
    {
        var direction = end - start;
        var part = CreatePart(name, parent, cylinderMesh, material,
            (start + end) * 0.5f,
            new Vector3(radius * 2f, direction.magnitude, radius * 2f),
            Quaternion.FromToRotation(Vector3.up, direction.normalized));
        part.GetComponent<MeshRenderer>().shadowCastingMode = ShadowCastingMode.Off;
    }

    static Transform CreateGroup(string name, Transform parent)
    {
        var group = new GameObject(name);
        group.transform.SetParent(parent, false);
        return group.transform;
    }

    static GameObject CreatePart(
        string name,
        Transform parent,
        Mesh mesh,
        Material material,
        Vector3 position,
        Vector3 scale,
        Quaternion rotation = default)
    {
        var part = new GameObject(name);
        part.transform.SetParent(parent, false);
        part.transform.localPosition = position;
        part.transform.localRotation = rotation == default ? Quaternion.identity : rotation;
        part.transform.localScale = scale;
        part.AddComponent<MeshFilter>().sharedMesh = mesh;
        var renderer = part.AddComponent<MeshRenderer>();
        renderer.sharedMaterial = material;
        renderer.shadowCastingMode = ShadowCastingMode.On;
        renderer.receiveShadows = true;
        return part;
    }

    static void ExportGlb(GameObject root)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(ExportPath));
        var settings = new ExportSettings
        {
            Format = GltfFormat.Binary,
            ImageDestination = ImageDestination.MainBuffer,
            FileConflictResolution = FileConflictResolution.Overwrite,
            Deterministic = true
        };
        var gameObjectSettings = new GameObjectExportSettings
        {
            OnlyActiveInHierarchy = true,
            DisabledComponents = false
        };
        var export = new GameObjectExport(settings, gameObjectSettings, logger: new ConsoleLogger());
        if (!export.AddScene(new[] { root }, "GJH Chibi Visitor"))
            throw new InvalidOperationException("glTFast reported a failure while collecting the character hierarchy.");

        var exportTask = export.SaveToFileAndDispose(Path.GetFullPath(ExportPath), forceSync: true);
        if (!exportTask.IsCompleted)
            throw new InvalidOperationException("The synchronous glTFast Editor export did not complete synchronously.");
        if (!exportTask.GetAwaiter().GetResult())
            throw new InvalidOperationException("glTFast failed to write the GLB.");
    }

    static void RenderPreviews(GameObject root)
    {
        Directory.CreateDirectory("Previews");
        var oldAmbientMode = RenderSettings.ambientMode;
        var oldAmbientLight = RenderSettings.ambientLight;
        var oldAmbientIntensity = RenderSettings.ambientIntensity;
        var oldProbe = RenderSettings.ambientProbe;
        var oldActiveRenderTexture = RenderTexture.active;
        var oldAsyncCompilation = ShaderUtil.allowAsyncCompilation;
        var oldQualityPipeline = QualitySettings.renderPipeline;
        RenderPipelineAsset studioPipeline = null;
        var studioRendererData = new List<UnityEngine.Object>();
        var layers = new Dictionary<GameObject, int>();
        var previousLightStates = new Dictionary<Light, bool>();
        var lights = new List<GameObject>();
        GameObject cameraObject = null;
        RenderTexture renderTexture = null;
        Texture2D capture = null;
        try
        {
            foreach (var light in UnityEngine.Object.FindObjectsByType<Light>(FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                previousLightStates[light] = light.enabled;
                light.enabled = false;
            }
            // Isolate the capture from any existing scene geometry and lighting.
            foreach (var transform in root.GetComponentsInChildren<Transform>(true))
            {
                layers[transform.gameObject] = transform.gameObject.layer;
                transform.gameObject.layer = 31;
            }
            // A temporary copy keeps project post effects (notably a 0.3 m SSAO
            // radius) from darkening this one-meter product shot. Nothing is saved.
            if (GraphicsSettings.currentRenderPipeline != null)
            {
                studioPipeline = UnityEngine.Object.Instantiate(GraphicsSettings.currentRenderPipeline);
                var settings = new SerializedObject(studioPipeline);
                var rendererList = settings.FindProperty("m_RendererDataList");
                if (rendererList != null)
                    for (var i = 0; i < rendererList.arraySize; i++)
                    {
                        var reference = rendererList.GetArrayElementAtIndex(i);
                        if (reference.objectReferenceValue == null) continue;
                        var data = UnityEngine.Object.Instantiate(reference.objectReferenceValue);
                        studioRendererData.Add(data);
                        var rendererSettings = new SerializedObject(data);
                        var features = rendererSettings.FindProperty("m_RendererFeatures");
                        if (features != null) features.ClearArray();
                        rendererSettings.ApplyModifiedPropertiesWithoutUndo();
                        reference.objectReferenceValue = data;
                    }
                settings.ApplyModifiedPropertiesWithoutUndo();
                QualitySettings.renderPipeline = studioPipeline;
            }
            ShaderUtil.allowAsyncCompilation = false;
            cameraObject = new GameObject("ChibiPreviewCamera");
            var camera = cameraObject.AddComponent<Camera>();
            camera.enabled = false;
            camera.orthographic = true;
            camera.orthographicSize = 0.635f;
            camera.aspect = 1f;
            camera.nearClipPlane = 0.05f;
            camera.farClipPlane = 20f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = Color.clear;
            camera.cullingMask = 1 << 31;
            camera.allowHDR = true;
            camera.renderingPath = RenderingPath.Forward;
            lights.Add(CreatePreviewLight("StudioSoftKey", Color.white, 0.90f));
            lights.Add(CreatePreviewLight("StudioFill", Color.white, 0.35f));
            lights.Add(CreatePreviewLight("StudioRim", Color.white, 0.70f));
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = Color.white * 0.45f;
            RenderSettings.ambientIntensity = 1f;
            var probe = new SphericalHarmonicsL2();
            probe.AddAmbientLight(Color.white * 0.45f);
            RenderSettings.ambientProbe = probe;
            renderTexture = new RenderTexture(StudioRenderSize, StudioRenderSize, 24, RenderTextureFormat.ARGBHalf, RenderTextureReadWrite.Linear)
            {
                antiAliasing = 4,
                name = "GJH Chibi HDR Studio"
            };
            renderTexture.Create();
            camera.targetTexture = renderTexture;
            capture = new Texture2D(StudioRenderSize, StudioRenderSize, TextureFormat.RGBAFloat, false, true);
            RenderView(camera, lights, new Vector3(0f, 0.62f, 3.2f), new Vector3(0f, 0.51f, 0f), "front", capture);
            RenderView(camera, lights, new Vector3(3.2f, 0.62f, 0f), new Vector3(0f, 0.51f, 0f), "side", capture);
            RenderView(camera, lights, new Vector3(0f, 0.62f, -3.2f), new Vector3(0f, 0.51f, 0f), "back", capture);
            RenderView(camera, lights, new Vector3(2.55f, 1.04f, 3.5f), new Vector3(0f, 0.51f, 0f), "3q", capture);
        }
        finally
        {
            RenderTexture.active = oldActiveRenderTexture;
            ShaderUtil.allowAsyncCompilation = oldAsyncCompilation;
            QualitySettings.renderPipeline = oldQualityPipeline;
            if (studioPipeline != null) UnityEngine.Object.DestroyImmediate(studioPipeline);
            foreach (var data in studioRendererData) UnityEngine.Object.DestroyImmediate(data);
            if (capture != null) UnityEngine.Object.DestroyImmediate(capture);
            if (renderTexture != null)
            {
                renderTexture.Release();
                UnityEngine.Object.DestroyImmediate(renderTexture);
            }
            if (cameraObject != null) UnityEngine.Object.DestroyImmediate(cameraObject);
            foreach (var light in lights) UnityEngine.Object.DestroyImmediate(light);
            foreach (var pair in previousLightStates) if (pair.Key != null) pair.Key.enabled = pair.Value;
            foreach (var pair in layers) if (pair.Key != null) pair.Key.layer = pair.Value;
            RenderSettings.ambientMode = oldAmbientMode;
            RenderSettings.ambientLight = oldAmbientLight;
            RenderSettings.ambientIntensity = oldAmbientIntensity;
            RenderSettings.ambientProbe = oldProbe;
        }
    }

    static GameObject CreatePreviewLight(string name, Color color, float intensity)
    {
        var lightObject = new GameObject(name);
        var light = lightObject.AddComponent<Light>();
        light.type = LightType.Directional;
        light.color = color;
        light.intensity = intensity;
        light.shadows = LightShadows.Soft;
        light.shadowStrength = 0.24f;
        light.shadowBias = 0.015f;
        light.shadowNormalBias = 0.02f;
        light.cullingMask = 1 << 31;
        return lightObject;
    }

    static void RenderView(Camera camera, List<GameObject> lights, Vector3 position, Vector3 target, string fileName, Texture2D capture)
    {
        camera.transform.position = position;
        camera.transform.rotation = Quaternion.LookRotation(target - position, Vector3.up);
        lights[0].transform.rotation = camera.transform.rotation * Quaternion.Euler(32f, -38f, 0f);
        lights[1].transform.rotation = camera.transform.rotation * Quaternion.Euler(12f, 48f, 0f);
        lights[2].transform.rotation = camera.transform.rotation * Quaternion.Euler(25f, 165f, 0f);
        // Warm all material variants before capturing the first view in batch mode.
        for (var frame = 0; frame < 3; frame++)
        {
            if (GraphicsSettings.currentRenderPipeline != null)
            {
                var request = new RenderPipeline.StandardRequest { destination = camera.targetTexture, face = CubemapFace.Unknown, mipLevel = 0 };
                if (!RenderPipeline.SupportsRenderRequest(camera, request))
                    throw new InvalidOperationException("The active render pipeline does not support standard render requests.");
                RenderPipeline.SubmitRenderRequest(camera, request);
            }
            else camera.Render();
        }
        var previous = RenderTexture.active;
        RenderTexture.active = camera.targetTexture;
        capture.ReadPixels(new Rect(0, 0, StudioRenderSize, StudioRenderSize), 0, 0, false);
        capture.Apply(false, false);
        var samples = capture.GetPixels();
        var pixels = new Color[PreviewSize * PreviewSize];
        for (var y = 0; y < PreviewSize; y++)
            for (var x = 0; x < PreviewSize; x++)
            {
                var offset = y * 2 * StudioRenderSize + x * 2;
                var c = (samples[offset] + samples[offset + 1] + samples[offset + StudioRenderSize] + samples[offset + StudioRenderSize + 1]) * 0.25f;
                var alpha = c.a;
                if (alpha > 0.00001f) c /= alpha;
                c.a = alpha;
                pixels[y * PreviewSize + x] = c;
            }
        var glow = new Color[pixels.Length];
        for (var i = 0; i < pixels.Length; i++)
        {
            var c = pixels[i];
            // Bloom is derived from the actual HDR purple emitters, never painted eyes.
            if (c.b > 1.1f && c.b > c.r * 1.3f)
                glow[i] = new Color(c.r, c.g, c.b, 0f) * (Mathf.Clamp01(c.b - 1.1f) * c.a);
        }
        var nearGlow = BlurGlow(glow, 5);
        var farGlow = BlurGlow(nearGlow, 12);
        var bottom = ParseColor("#E4DCF2").linear;
        var top = ParseColor("#F3F0FA").linear;
        var foot = camera.WorldToViewportPoint(Vector3.zero);
        for (var y = 0; y < PreviewSize; y++)
            for (var x = 0; x < PreviewSize; x++)
            {
                var i = y * PreviewSize + x;
                var u = (x + 0.5f) / PreviewSize;
                var v = (y + 0.5f) / PreviewSize;
                var background = Color.Lerp(bottom, top, Mathf.SmoothStep(0f, 1f, v));
                var vignette = (u - 0.5f) * (u - 0.5f) * 0.045f;
                background *= 1f - vignette;
                // Seamless cyclorama contact shadow, outside the exported character.
                var shadow = Mathf.Exp(-Mathf.Pow((u - foot.x) / 0.155f, 2f) - Mathf.Pow((v - foot.y - 0.003f) / 0.021f, 2f));
                background *= 1f - shadow * 0.22f;
                var c = pixels[i];
                var alpha = Mathf.Clamp01(c.a);
                // Compress highlights together so bright violet keeps its hue.
                var peak = Mathf.Max(c.r, Mathf.Max(c.g, c.b));
                if (peak > 0.8f) c *= SoftHighlight(peak) / peak;
                c = Color.Lerp(background, c, alpha) + nearGlow[i] * 0.16f + farGlow[i] * 0.18f;
                c = c.gamma;
                c.a = 1f;
                pixels[i] = c;
            }
        var output = new Texture2D(PreviewSize, PreviewSize, TextureFormat.RGB24, false, false);
        output.SetPixels(pixels);
        output.Apply(false, false);
        File.WriteAllBytes(Path.Combine("Previews", fileName + ".png"), output.EncodeToPNG());
        UnityEngine.Object.DestroyImmediate(output);
        RenderTexture.active = previous;
        Debug.Log($"[ChibiBuilder] Rendered Previews/{fileName}.png");
    }

    static float SoftHighlight(float linear)
    {
        return linear <= 0.8f ? Mathf.Max(0f, linear) : 0.8f + 0.2f * (1f - Mathf.Exp(-(linear - 0.8f) / 0.2f));
    }

    static Color[] BlurGlow(Color[] input, int radius)
    {
        var temporary = new Color[input.Length];
        var output = new Color[input.Length];
        var weights = new float[radius * 2 + 1];
        var sum = 0f;
        for (var i = -radius; i <= radius; i++)
        {
            weights[i + radius] = Mathf.Exp(-i * i / (2f * radius * radius * 0.25f));
            sum += weights[i + radius];
        }
        for (var i = 0; i < weights.Length; i++) weights[i] /= sum;
        for (var y = 0; y < PreviewSize; y++)
            for (var x = 0; x < PreviewSize; x++)
                for (var d = -radius; d <= radius; d++)
                    temporary[y * PreviewSize + x] += input[y * PreviewSize + Mathf.Clamp(x + d, 0, PreviewSize - 1)] * weights[d + radius];
        for (var y = 0; y < PreviewSize; y++)
            for (var x = 0; x < PreviewSize; x++)
                for (var d = -radius; d <= radius; d++)
                    output[y * PreviewSize + x] += temporary[Mathf.Clamp(y + d, 0, PreviewSize - 1) * PreviewSize + x] * weights[d + radius];
        return output;
    }

    static string FormatVector(Vector3 value)
    {
        return $"({value.x:F4}, {value.y:F4}, {value.z:F4})";
    }

    static void EnsureProjectFolders()
    {
        EnsureFolder("Assets", "Chibi");
        EnsureFolder(AssetRoot, "Meshes");
        EnsureFolder(AssetRoot, "Materials");
        EnsureFolder(AssetRoot, "Prefabs");
        Directory.CreateDirectory("Exports");
        Directory.CreateDirectory("Previews");
    }

    static void EnsureFolder(string parent, string child)
    {
        var path = parent + "/" + child;
        if (!AssetDatabase.IsValidFolder(path))
            AssetDatabase.CreateFolder(parent, child);
    }

    static void LoadOrCreateAssets()
    {
        sphereMesh = SaveMeshAsset("LowPolySphere", CreateSphereMesh(16, 10));
        helmetMesh = SaveMeshAsset("PillowShell", CreatePillowMesh(32, 18, 0.72f));
        lensMesh = SaveMeshAsset("RoundedVisor", CreateLensMesh());
        detailMesh = SaveMeshAsset("SoftDetail", CreateSphereMesh(10, 8));
        clothMesh = SaveMeshAsset("PuffyCloth", CreateRoundedBoxMesh(6, 0.32f));
        cubeMesh = SaveMeshAsset("SharpCube", CreateCubeMesh());
        roundedBoxMesh = SaveMeshAsset("SoftRoundedBox", CreateRoundedBoxMesh(4, 0.30f));
        cylinderMesh = SaveMeshAsset("LowPolyCylinder", CreateCylinderMesh(8));
        torusMesh = SaveMeshAsset("Torus", CreateTorusMesh(32, 8, 0.5f, 0.085f));
        finMesh = SaveMeshAsset("EarFin", CreateFinMesh());
        heartWedgeMesh = SaveMeshAsset("HeartWedge", CreateHeartWedgeMesh());

        whiteMaterial = SaveMaterial("White", "#F4F2FA", 0f, 0.28f, null);
        darkMaterial = SaveMaterial("NearBlack", "#2A2838", 0.05f, 0.24f, null);
        glassMaterial = SaveMaterial("GlossyFaceGlass", "#100F18", 0.08f, 0.75f, null);
        purpleMaterial = SaveMaterial("Purple", "#8B5CF6", 0f, 0.34f, null);
        purpleGlowMaterial = SaveMaterial("PurpleEmission", "#8B5CF6", 0f, 0.28f, "#8B5CF6");
        lavenderMaterial = SaveMaterial("LightLavender", "#D9CCF7", 0f, 0.32f, null);
        seamMaterial = SaveMaterial("PocketSeam", "#B9AFCC", 0f, 0.2f, null);
        reflectionMaterial = SaveMaterial("GlassReflection", "#424054", 0f, 0.6f, null);
    }

    static Material SaveMaterial(string name, string baseHex, float metallic, float smoothness, string emissionHex)
    {
        var path = MaterialFolder + "/" + name + ".mat";
        var material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (material == null)
        {
            var shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
            if (shader == null)
                throw new InvalidOperationException("No compatible lit shader was found.");
            material = new Material(shader) { name = name };
            AssetDatabase.CreateAsset(material, path);
        }

        var baseColor = ParseColor(baseHex);
        if (material.HasProperty("_BaseColor"))
            material.SetColor("_BaseColor", baseColor);
        if (material.HasProperty("_Color"))
            material.SetColor("_Color", baseColor);
        if (material.HasProperty("_Metallic"))
            material.SetFloat("_Metallic", metallic);
        if (material.HasProperty("_Smoothness"))
            material.SetFloat("_Smoothness", smoothness);
        if (material.HasProperty("_Glossiness"))
            material.SetFloat("_Glossiness", smoothness);
        if (material.HasProperty("_SpecColor"))
            material.SetColor("_SpecColor", new Color(0.04f, 0.04f, 0.04f, 1f));
        if (material.HasProperty("_SpecularHighlights"))
            material.SetFloat("_SpecularHighlights", name == "PurpleEmission" ? 0f : 1f);
        if (material.HasProperty("_EnvironmentReflections") && (name == "GlossyFaceGlass" || name == "PurpleEmission"))
            material.SetFloat("_EnvironmentReflections", 0f);

        if (!string.IsNullOrEmpty(emissionHex) && material.HasProperty("_EmissionColor"))
        {
            var emissionColor = ParseColor(emissionHex) * 2.4f;
            emissionColor.a = 1f;
            material.SetColor("_EmissionColor", emissionColor);
            material.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
            var emissionKeyword = new LocalKeyword(material.shader, "_EMISSION");
            if (emissionKeyword.isValid)
                material.SetKeyword(emissionKeyword, true);
            else
                material.EnableKeyword("_EMISSION");
        }
        else if (material.HasProperty("_EmissionColor"))
        {
            material.SetColor("_EmissionColor", Color.black);
            material.globalIlluminationFlags = MaterialGlobalIlluminationFlags.EmissiveIsBlack;
            var emissionKeyword = new LocalKeyword(material.shader, "_EMISSION");
            if (emissionKeyword.isValid)
                material.SetKeyword(emissionKeyword, false);
            else
                material.DisableKeyword("_EMISSION");
        }

        EditorUtility.SetDirty(material);
        return material;
    }

    static Color ParseColor(string html)
    {
        if (!ColorUtility.TryParseHtmlString(html, out var color))
            throw new InvalidOperationException("Invalid color " + html);
        return color;
    }

    static Mesh SaveMeshAsset(string name, Mesh generated)
    {
        generated.name = name;
        var path = MeshFolder + "/" + name + ".asset";
        var existing = AssetDatabase.LoadAssetAtPath<Mesh>(path);
        if (existing == null)
        {
            generated.UploadMeshData(false);
            AssetDatabase.CreateAsset(generated, path);
            return generated;
        }

        // Replace mesh buffers through the Mesh API. CopySerialized can leave stale
        // GPU vertex/index layouts when a repeated build changes the topology.
        existing.Clear(false);
        existing.indexFormat = generated.indexFormat;
        existing.vertices = generated.vertices;
        existing.normals = generated.normals;
        existing.triangles = generated.triangles;
        existing.RecalculateBounds();
        existing.UploadMeshData(false);
        existing.name = name;
        EditorUtility.SetDirty(existing);
        UnityEngine.Object.DestroyImmediate(generated);
        return existing;
    }

    static Mesh CreateSphereMesh(int longitudeSegments, int latitudeSegments)
    {
        var vertices = new List<Vector3>();
        var normals = new List<Vector3>();
        var triangles = new List<int>();
        vertices.Add(Vector3.up * 0.5f);
        normals.Add(Vector3.up);

        for (var lat = 1; lat < latitudeSegments; lat++)
        {
            var theta = Mathf.PI * lat / latitudeSegments;
            var ringRadius = Mathf.Sin(theta) * 0.5f;
            var y = Mathf.Cos(theta) * 0.5f;
            for (var lon = 0; lon < longitudeSegments; lon++)
            {
                var phi = 2f * Mathf.PI * lon / longitudeSegments;
                var vertex = new Vector3(ringRadius * Mathf.Cos(phi), y, ringRadius * Mathf.Sin(phi));
                vertices.Add(vertex);
                normals.Add(vertex.normalized);
            }
        }

        var bottomIndex = vertices.Count;
        vertices.Add(Vector3.down * 0.5f);
        normals.Add(Vector3.down);

        for (var lon = 0; lon < longitudeSegments; lon++)
        {
            var next = (lon + 1) % longitudeSegments;
            AddTriangleOutward(vertices, triangles, 0, 1 + next, 1 + lon, Vector3.up);
        }

        var ringCount = latitudeSegments - 1;
        for (var ring = 0; ring < ringCount - 1; ring++)
        {
            var first = 1 + ring * longitudeSegments;
            var second = first + longitudeSegments;
            for (var lon = 0; lon < longitudeSegments; lon++)
            {
                var next = (lon + 1) % longitudeSegments;
                var a = first + lon;
                var b = second + lon;
                var c = second + next;
                var d = first + next;
                var outward = (vertices[a] + vertices[b] + vertices[c] + vertices[d]).normalized;
                AddTriangleOutward(vertices, triangles, a, d, c, outward);
                AddTriangleOutward(vertices, triangles, a, c, b, outward);
            }
        }

        var lastRing = 1 + (ringCount - 1) * longitudeSegments;
        for (var lon = 0; lon < longitudeSegments; lon++)
        {
            var next = (lon + 1) % longitudeSegments;
            AddTriangleOutward(vertices, triangles, lastRing + lon, lastRing + next, bottomIndex, Vector3.down);
        }

        var mesh = new Mesh { vertices = vertices.ToArray(), normals = normals.ToArray() };
        mesh.SetTriangles(triangles, 0);
        mesh.RecalculateBounds();
        return mesh;
    }

    static void AddTriangleOutward(List<Vector3> vertices, List<int> triangles, int a, int b, int c, Vector3 expectedNormal)
    {
        var cross = Vector3.Cross(vertices[b] - vertices[a], vertices[c] - vertices[a]);
        if (Vector3.Dot(cross, expectedNormal) >= 0f)
        {
            triangles.Add(a);
            triangles.Add(b);
            triangles.Add(c);
        }
        else
        {
            triangles.Add(a);
            triangles.Add(c);
            triangles.Add(b);
        }
    }

    static Mesh CreateCubeMesh()
    {
        var vertices = new List<Vector3>();
        var normals = new List<Vector3>();
        var triangles = new List<int>();
        AddCubeFace(vertices, normals, triangles, new Vector3(-0.5f, -0.5f, 0.5f), Vector3.right, Vector3.up, Vector3.forward);
        AddCubeFace(vertices, normals, triangles, new Vector3(0.5f, -0.5f, -0.5f), Vector3.left, Vector3.up, Vector3.back);
        AddCubeFace(vertices, normals, triangles, new Vector3(0.5f, -0.5f, 0.5f), Vector3.back, Vector3.up, Vector3.right);
        AddCubeFace(vertices, normals, triangles, new Vector3(-0.5f, -0.5f, -0.5f), Vector3.forward, Vector3.up, Vector3.left);
        AddCubeFace(vertices, normals, triangles, new Vector3(-0.5f, 0.5f, 0.5f), Vector3.right, Vector3.back, Vector3.up);
        AddCubeFace(vertices, normals, triangles, new Vector3(-0.5f, -0.5f, -0.5f), Vector3.right, Vector3.forward, Vector3.down);
        var mesh = new Mesh { vertices = vertices.ToArray(), normals = normals.ToArray() };
        mesh.SetTriangles(triangles, 0);
        mesh.RecalculateBounds();
        return mesh;
    }

    static void AddCubeFace(List<Vector3> vertices, List<Vector3> normals, List<int> triangles, Vector3 origin, Vector3 u, Vector3 v, Vector3 normal)
    {
        var start = vertices.Count;
        vertices.Add(origin);
        vertices.Add(origin + u);
        vertices.Add(origin + u + v);
        vertices.Add(origin + v);
        normals.Add(normal);
        normals.Add(normal);
        normals.Add(normal);
        normals.Add(normal);
        triangles.Add(start);
        triangles.Add(start + 1);
        triangles.Add(start + 2);
        triangles.Add(start);
        triangles.Add(start + 2);
        triangles.Add(start + 3);
    }

    static Mesh CreateRoundedBoxMesh(int subdivisions, float bevel)
    {
        var vertices = new List<Vector3>();
        var normals = new List<Vector3>();
        var triangles = new List<int>();
        var faces = new[]
        {
            new FaceFrame(new Vector3(-0.5f, -0.5f, 0.5f), Vector3.right, Vector3.up),
            new FaceFrame(new Vector3(0.5f, -0.5f, -0.5f), Vector3.left, Vector3.up),
            new FaceFrame(new Vector3(0.5f, -0.5f, 0.5f), Vector3.back, Vector3.up),
            new FaceFrame(new Vector3(-0.5f, -0.5f, -0.5f), Vector3.forward, Vector3.up),
            new FaceFrame(new Vector3(-0.5f, 0.5f, 0.5f), Vector3.right, Vector3.back),
            new FaceFrame(new Vector3(-0.5f, -0.5f, -0.5f), Vector3.right, Vector3.forward)
        };

        foreach (var face in faces)
        {
            var start = vertices.Count;
            for (var y = 0; y <= subdivisions; y++)
            {
                for (var x = 0; x <= subdivisions; x++)
                {
                    var raw = face.origin + face.u * (x / (float)subdivisions) + face.v * (y / (float)subdivisions);
                    var core = new Vector3(
                        Mathf.Clamp(raw.x, -0.5f + bevel, 0.5f - bevel),
                        Mathf.Clamp(raw.y, -0.5f + bevel, 0.5f - bevel),
                        Mathf.Clamp(raw.z, -0.5f + bevel, 0.5f - bevel));
                    var normal = (raw - core).normalized;
                    vertices.Add(core + normal * bevel);
                    normals.Add(normal);
                }
            }

            var row = subdivisions + 1;
            for (var y = 0; y < subdivisions; y++)
            {
                for (var x = 0; x < subdivisions; x++)
                {
                    var a = start + y * row + x;
                    var b = a + 1;
                    var d = a + row;
                    var c = d + 1;
                    triangles.Add(a);
                    triangles.Add(b);
                    triangles.Add(c);
                    triangles.Add(a);
                    triangles.Add(c);
                    triangles.Add(d);
                }
            }
        }

        var mesh = new Mesh { vertices = vertices.ToArray(), normals = normals.ToArray() };
        mesh.SetTriangles(triangles, 0);
        mesh.RecalculateBounds();
        return mesh;
    }

    struct FaceFrame
    {
        public Vector3 origin;
        public Vector3 u;
        public Vector3 v;

        public FaceFrame(Vector3 origin, Vector3 u, Vector3 v)
        {
            this.origin = origin;
            this.u = u;
            this.v = v;
        }
    }

    static Mesh CreateCylinderMesh(int sides)
    {
        var vertices = new List<Vector3>();
        var normals = new List<Vector3>();
        var triangles = new List<int>();
        var sideStart = vertices.Count;
        for (var ring = 0; ring < 2; ring++)
        {
            var y = ring == 0 ? -0.5f : 0.5f;
            for (var i = 0; i < sides; i++)
            {
                var angle = i * 2f * Mathf.PI / sides;
                var normal = new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle));
                vertices.Add(new Vector3(normal.x * 0.5f, y, normal.z * 0.5f));
                normals.Add(normal);
            }
        }

        for (var i = 0; i < sides; i++)
        {
            var next = (i + 1) % sides;
            var bottom = sideStart + i;
            var bottomNext = sideStart + next;
            var top = sideStart + sides + i;
            var topNext = sideStart + sides + next;
            triangles.Add(bottom);
            triangles.Add(top);
            triangles.Add(topNext);
            triangles.Add(bottom);
            triangles.Add(topNext);
            triangles.Add(bottomNext);
        }

        AddCylinderCap(vertices, normals, triangles, sides, -0.5f, Vector3.down);
        AddCylinderCap(vertices, normals, triangles, sides, 0.5f, Vector3.up);
        var mesh = new Mesh { vertices = vertices.ToArray(), normals = normals.ToArray() };
        mesh.SetTriangles(triangles, 0);
        mesh.RecalculateBounds();
        return mesh;
    }

    static void AddCylinderCap(List<Vector3> vertices, List<Vector3> normals, List<int> triangles, int sides, float y, Vector3 normal)
    {
        var center = vertices.Count;
        vertices.Add(new Vector3(0f, y, 0f));
        normals.Add(normal);
        var ring = vertices.Count;
        for (var i = 0; i < sides; i++)
        {
            var angle = i * 2f * Mathf.PI / sides;
            vertices.Add(new Vector3(Mathf.Cos(angle) * 0.5f, y, Mathf.Sin(angle) * 0.5f));
            normals.Add(normal);
        }
        for (var i = 0; i < sides; i++)
        {
            var next = (i + 1) % sides;
            if (normal.y > 0f)
            {
                triangles.Add(center);
                triangles.Add(ring + next);
                triangles.Add(ring + i);
            }
            else
            {
                triangles.Add(center);
                triangles.Add(ring + i);
                triangles.Add(ring + next);
            }
        }
    }

    static Mesh CreateTorusMesh(int majorSegments, int minorSegments, float majorRadius, float tubeRadius)
    {
        var vertices = new Vector3[majorSegments * minorSegments];
        var normals = new Vector3[vertices.Length];
        var triangles = new List<int>(majorSegments * minorSegments * 6);
        for (var major = 0; major < majorSegments; major++)
        {
            var u = major * 2f * Mathf.PI / majorSegments;
            var cosU = Mathf.Cos(u);
            var sinU = Mathf.Sin(u);
            for (var minor = 0; minor < minorSegments; minor++)
            {
                var v = minor * 2f * Mathf.PI / minorSegments;
                var cosV = Mathf.Cos(v);
                var sinV = Mathf.Sin(v);
                var index = major * minorSegments + minor;
                vertices[index] = new Vector3((majorRadius + tubeRadius * cosV) * cosU,
                    (majorRadius + tubeRadius * cosV) * sinU, tubeRadius * sinV);
                normals[index] = new Vector3(cosV * cosU, cosV * sinU, sinV).normalized;
            }
        }

        for (var major = 0; major < majorSegments; major++)
        {
            var nextMajor = (major + 1) % majorSegments;
            for (var minor = 0; minor < minorSegments; minor++)
            {
                var nextMinor = (minor + 1) % minorSegments;
                var a = major * minorSegments + minor;
                var b = nextMajor * minorSegments + minor;
                var c = nextMajor * minorSegments + nextMinor;
                var d = major * minorSegments + nextMinor;
                triangles.Add(a);
                triangles.Add(b);
                triangles.Add(c);
                triangles.Add(a);
                triangles.Add(c);
                triangles.Add(d);
            }
        }

        var mesh = new Mesh { vertices = vertices, normals = normals };
        mesh.SetTriangles(triangles, 0);
        mesh.RecalculateBounds();
        return mesh;
    }

    static Mesh CreateFinMesh()
    {
        // A beveled, swept blade rather than a flat triangular cat ear.
        var outline = new[] {
            new Vector2(-0.40f, 0f), new Vector2(0.40f, 0f),
            new Vector2(0.43f, 0.14f), new Vector2(0.29f, 0.48f),
            new Vector2(0.12f, 0.86f), new Vector2(0f, 1f),
            new Vector2(-0.08f, 0.93f), new Vector2(-0.27f, 0.62f),
            new Vector2(-0.46f, 0.20f) };
        var vertices = new List<Vector3>();
        var triangles = new List<int>();
        var center = new Vector2(0f, 0.36f);
        var scales = new[] { 0.81f, 1f, 1f, 0.81f };
        var depths = new[] { -0.5f, -0.27f, 0.27f, 0.5f };
        for (var ring = 0; ring < scales.Length; ring++)
            foreach (var point in outline)
            {
                var v = center + (point - center) * scales[ring];
                vertices.Add(new Vector3(v.x, v.y, depths[ring] - v.y * 0.45f));
            }
        var count = outline.Length;
        for (var ring = 0; ring < 3; ring++)
            for (var i = 0; i < count; i++)
            {
                var a = ring * count + i;
                var b = ring * count + (i + 1) % count;
                triangles.AddRange(new[] { a, b, b + count, a, b + count, a + count });
            }
        for (var i = 1; i < count - 1; i++)
        {
            triangles.AddRange(new[] { 0, i + 1, i });
            triangles.AddRange(new[] { 3 * count, 3 * count + i, 3 * count + i + 1 });
        }
        var mesh = new Mesh { vertices = vertices.ToArray(), triangles = triangles.ToArray() };
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
        return mesh;
    }

    static Mesh CreatePillowMesh(int longitude, int latitude, float exponent)
    {
        var mesh = CreateSphereMesh(longitude, latitude);
        var vertices = mesh.vertices;
        var normals = mesh.normals;
        for (var i = 0; i < vertices.Length; i++)
        {
            var v = vertices[i] * 2f;
            v = new Vector3(SignedPower(v.x, exponent), SignedPower(v.y, exponent), SignedPower(v.z, exponent));
            // Recess the helmet's front under the curved visor, avoiding shell
            // intersections while preserving the full rounded back silhouette.
            vertices[i] = new Vector3(v.x, v.y, v.z > 0f ? v.z * 0.8f : v.z) * 0.5f;
            var power = 2f / exponent - 1f;
            normals[i] = new Vector3(SignedPower(v.x, power), SignedPower(v.y, power),
                SignedPower(v.z, power) / (v.z > 0f ? 0.8f : 1f)).normalized;
        }
        mesh.vertices = vertices;
        mesh.normals = normals;
        mesh.RecalculateBounds();
        return mesh;
    }

    static float SignedPower(float value, float power)
    {
        return Mathf.Sign(value) * Mathf.Pow(Mathf.Abs(value), power);
    }

    static Mesh CreateLensMesh()
    {
        const int count = 40;
        var vertices = new List<Vector3>();
        var triangles = new List<int>();
        var scales = new[] { 0.94f, 1f, 0.97f, 0.80f };
        var depths = new[] { -0.5f, -0.16f, 0.30f, 0.47f };
        for (var ring = 0; ring < scales.Length; ring++)
            for (var i = 0; i < count; i++)
            {
                var corner = i / 10;
                var angle = (corner * 90f + i % 10 * 10f) * Mathf.Deg2Rad;
                var center = new Vector2(corner == 0 || corner == 3 ? 0.24f : -0.24f,
                    corner < 2 ? 0.24f : -0.24f);
                var point = center + new Vector2(Mathf.Cos(angle), Mathf.Sin(angle)) * 0.26f;
                vertices.Add(new Vector3(point.x * scales[ring], point.y * scales[ring], depths[ring]));
            }
        for (var ring = 0; ring < scales.Length - 1; ring++)
            for (var i = 0; i < count; i++)
            {
                var a = ring * count + i;
                var b = ring * count + (i + 1) % count;
                triangles.AddRange(new[] { a, b, b + count, a, b + count, a + count });
            }
        var front = vertices.Count;
        vertices.Add(new Vector3(0f, 0f, 0.5f));
        var back = vertices.Count;
        vertices.Add(new Vector3(0f, 0f, -0.5f));
        for (var i = 0; i < count; i++)
        {
            var next = (i + 1) % count;
            triangles.AddRange(new[] { front, 3 * count + i, 3 * count + next, back, next, i });
        }
        var mesh = new Mesh { vertices = vertices.ToArray(), triangles = triangles.ToArray() };
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
        return mesh;
    }

    static void CreateCurve(Transform parent, string name, Vector3[] points, float radius, Material material)
    {
        const int sides = 8;
        var vertices = new List<Vector3>();
        var normals = new List<Vector3>();
        var triangles = new List<int>();
        // Rounded end caps and a continuous tube keep the smile and eye arcs soft.
        var centers = new List<Vector3> { points[0] - (points[1] - points[0]).normalized * radius };
        centers.AddRange(points);
        centers.Add(points[points.Length - 1] + (points[points.Length - 1] - points[points.Length - 2]).normalized * radius);
        for (var ring = 0; ring < centers.Count; ring++)
        {
            var tangent = (centers[Mathf.Min(ring + 1, centers.Count - 1)] - centers[Mathf.Max(ring - 1, 0)]).normalized;
            var across = Vector3.Cross(tangent, Vector3.forward).normalized;
            var cap = ring == 0 || ring == centers.Count - 1;
            for (var j = 0; j < sides; j++)
            {
                var angle = j * Mathf.PI * 2f / sides;
                var normal = across * Mathf.Cos(angle) + Vector3.forward * Mathf.Sin(angle);
                vertices.Add(centers[ring] + normal * (cap ? radius * 0.05f : radius));
                normals.Add(cap ? (ring == 0 ? -tangent : tangent) : normal);
            }
        }
        for (var ring = 0; ring < centers.Count - 1; ring++)
            for (var j = 0; j < sides; j++)
            {
                var a = ring * sides + j;
                var b = ring * sides + (j + 1) % sides;
                var outward = normals[a] + normals[b];
                AddTriangleOutward(vertices, triangles, a, b, b + sides, outward);
                AddTriangleOutward(vertices, triangles, a, b + sides, a + sides, outward);
            }
        for (var j = 1; j < sides - 1; j++)
        {
            AddTriangleOutward(vertices, triangles, 0, j, j + 1, normals[0]);
            var end = (centers.Count - 1) * sides;
            AddTriangleOutward(vertices, triangles, end, end + j, end + j + 1, normals[end]);
        }
        var mesh = new Mesh { vertices = vertices.ToArray(), normals = normals.ToArray(), triangles = triangles.ToArray() };
        mesh.RecalculateBounds();
        mesh = SaveMeshAsset(parent.name + "_" + name, mesh);
        var part = CreatePart(name, parent, mesh, material, Vector3.zero, Vector3.one);
        part.GetComponent<MeshRenderer>().shadowCastingMode = ShadowCastingMode.Off;
    }

    static Mesh CreateHeartWedgeMesh()
    {
        var vertices = new[]
        {
            new Vector3(-0.5f, 0.12f, 0.5f), new Vector3(0.5f, 0.12f, 0.5f), new Vector3(0f, -0.5f, 0.5f),
            new Vector3(-0.5f, 0.12f, -0.5f), new Vector3(0.5f, 0.12f, -0.5f), new Vector3(0f, -0.5f, -0.5f)
        };
        var triangles = new[]
        {
            0, 1, 2, 5, 4, 3,
            0, 5, 3, 0, 2, 5,
            1, 4, 5, 1, 5, 2,
            0, 3, 4, 0, 4, 1
        };
        for (var i = 0; i < triangles.Length; i += 3)
        {
            var temporary = triangles[i + 1];
            triangles[i + 1] = triangles[i + 2];
            triangles[i + 2] = temporary;
        }
        var mesh = new Mesh { vertices = vertices };
        mesh.triangles = triangles;
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
        return mesh;
    }
}
