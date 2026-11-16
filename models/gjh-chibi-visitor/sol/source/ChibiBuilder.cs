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

    static Mesh sphereMesh;
    static Mesh cubeMesh;
    static Mesh roundedBoxMesh;
    static Mesh helmetMesh;
    static Mesh screenMesh;
    static Mesh hoodieMesh;
    static Mesh detailBoxMesh;
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
    static Material screenGlintMaterial;

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
        // Ceramic toy proportions: a 0.48 m helmet over a compact 0.43 m body.
        var head = CreateGroup("Head", root.transform);
        CreatePart("HelmetShell", head, helmetMesh, whiteMaterial,
            new Vector3(0f, 0.67f, 0f), new Vector3(0.61f, 0.48f, 0.43f));

        var face = CreateGroup("Face", root.transform);
        CreatePart("ScreenBezel", face, screenMesh, darkMaterial,
            new Vector3(0f, 0.666f, 0.185f), new Vector3(0.534f, 0.345f, 0.096f));
        CreatePart("GlossyFaceScreen", face, screenMesh, glassMaterial,
            new Vector3(0f, 0.666f, 0.222f), new Vector3(0.505f, 0.316f, 0.048f));
        var eyes = CreateGroup("Eyes", face);
        eyes.localPosition = new Vector3(0f, 0.678f, 0.249f);
        CreateExpressions(eyes);
        CreateStroke(face, "GlassSoftboxReflection", new Vector3(0.137f, 0.786f, 0.244f),
            new Vector3(0.189f, 0.780f, 0.242f), 0.003f, screenGlintMaterial);
        CreateStroke(face, "GlassReflectionDot", new Vector3(0.202f, 0.772f, 0.238f),
            new Vector3(0.207f, 0.767f, 0.237f), 0.002f, screenGlintMaterial);

        var ears = CreateGroup("Ears", root.transform);
        CreateEar(ears, "LeftEarFin", -1f);
        CreateEar(ears, "RightEarFin", 1f);
        var headphones = CreateGroup("Headphones", root.transform);
        CreateHeadphone(headphones, "LeftHeadphone", -1f);
        CreateHeadphone(headphones, "RightHeadphone", 1f);

        var outfit = CreateGroup("Outfit", root.transform);
        CreatePart("HoodieTorso", outfit, hoodieMesh, whiteMaterial,
            new Vector3(0f, 0.322f, 0f), new Vector3(0.335f, 0.238f, 0.238f));
        CreatePart("FoldedHood", outfit, sphereMesh, purpleMaterial,
            new Vector3(0f, 0.426f, -0.103f), new Vector3(0.29f, 0.157f, 0.19f));
        CreatePart("HoodCollarRoll", outfit, torusMesh, purpleMaterial,
            new Vector3(0f, 0.428f, 0.006f), new Vector3(0.251f, 0.198f, 0.16f),
            Quaternion.Euler(90f, 0f, 0f));
        CreateSleeve(outfit, "LeftSleeve", -1f);
        CreateSleeve(outfit, "RightSleeve", 1f);
        CreateLogo(outfit);
        CreatePart("KangarooPocket", outfit, screenMesh, whiteMaterial,
            new Vector3(0f, 0.259f, 0.121f), new Vector3(0.191f, 0.065f, 0.016f));
        CreateStroke(outfit, "PocketLeftOpening", new Vector3(-0.088f, 0.274f, 0.129f),
            new Vector3(-0.063f, 0.256f, 0.13f), 0.002f, lavenderMaterial);
        CreateStroke(outfit, "PocketRightOpening", new Vector3(0.088f, 0.274f, 0.129f),
            new Vector3(0.063f, 0.256f, 0.13f), 0.002f, lavenderMaterial);
        CreatePart("HoodieRibbedHem", outfit, detailBoxMesh, whiteMaterial,
            new Vector3(0f, 0.223f, 0f), new Vector3(0.27f, 0.036f, 0.206f));

        var legs = CreateGroup("Legs", root.transform);
        var hands = CreateGroup("Hands", root.transform);
        var feet = CreateGroup("Feet", root.transform);
        foreach (var side in new[] { -1f, 1f })
        {
            var label = side < 0f ? "Left" : "Right";
            CreatePart(label + "ShortsLeg", outfit, detailBoxMesh, darkMaterial,
                new Vector3(side * 0.079f, 0.194f, -0.006f), new Vector3(0.151f, 0.114f, 0.191f));
            CreatePart(label + "ShortsPurpleHem", outfit, detailBoxMesh, purpleMaterial,
                new Vector3(side * 0.079f, 0.148f, -0.006f), new Vector3(0.149f, 0.023f, 0.19f));
            CreatePart(label + "Leg", legs, detailBoxMesh, whiteMaterial,
                new Vector3(side * 0.083f, 0.124f, 0f), new Vector3(0.113f, 0.128f, 0.129f));
            CreatePart(label + "SquareLegPatch", legs, detailBoxMesh, purpleMaterial,
                new Vector3(side * 0.083f, 0.111f, 0.066f), new Vector3(0.044f, 0.044f, 0.012f));
            CreatePart(label + "Mitten", hands, sphereMesh, darkMaterial,
                new Vector3(side * 0.253f, 0.238f, 0.019f), new Vector3(0.103f, 0.104f, 0.108f),
                Quaternion.Euler(0f, 0f, side * 15f));
            CreatePart(label + "MittenThumb", hands, sphereMesh, darkMaterial,
                new Vector3(side * 0.218f, 0.248f, 0.052f), new Vector3(0.044f, 0.055f, 0.051f));
            CreatePart(label + "Shoe", feet, sphereMesh, darkMaterial,
                new Vector3(side * 0.086f, 0.047f, 0.027f), new Vector3(0.146f, 0.094f, 0.181f));
            CreatePart(label + "HeelTab", feet, detailBoxMesh, purpleMaterial,
                new Vector3(side * 0.086f, 0.052f, -0.062f), new Vector3(0.043f, 0.025f, 0.009f));
        }
        var headTilt = Quaternion.Euler(0f, 0f, -2f);
        var headPivot = new Vector3(0f, 0.67f, 0f);
        foreach (var module in new[] { head, face, ears, headphones })
        {
            module.localRotation = headTilt;
            module.localPosition = headPivot - headTilt * headPivot;
        }
        return root;
    }

    static void CreateExpressions(Transform eyes)
    {
        var happy = CreateGroup("Happy", eyes);
        foreach (var x in new[] { -0.108f, 0.108f })
        {
            var points = new List<Vector3>();
            // A softly rounded caret keeps the happy expression readable at thumbnail size.
            for (var i = 0; i <= 12; i++)
            {
                var t = i / 12f;
                points.Add(new Vector3(x + Mathf.Lerp(-0.05f, 0.05f, t),
                    -0.006f + 0.057f * Mathf.Sin(Mathf.PI * t), 0f));
            }
            CreateTube(happy, x < 0f ? "LeftHappyArc" : "RightHappyArc", points, 0.009f, purpleGlowMaterial);
        }
        var smile = new List<Vector3>();
        for (var i = 0; i <= 10; i++)
        {
            var t = i / 10f;
            smile.Add(new Vector3(Mathf.Lerp(-0.031f, 0.031f, t),
                -0.073f - 0.013f * Mathf.Sin(Mathf.PI * t), 0f));
        }
        CreateTube(happy, "TinySmile", smile, 0.0045f, purpleGlowMaterial);
        CreateStroke(happy, "LeftCheek", new Vector3(-0.179f, -0.053f, -0.001f),
            new Vector3(-0.157f, -0.053f, -0.001f), 0.0035f, purpleMaterial);
        CreateStroke(happy, "RightCheek", new Vector3(0.157f, -0.053f, -0.001f),
            new Vector3(0.179f, -0.053f, -0.001f), 0.0035f, purpleMaterial);
        happy.gameObject.SetActive(true);

        var sleep = CreateGroup("Sleep", eyes);
        CreateStroke(sleep, "LeftSleepEye", new Vector3(-0.158f, 0.014f, 0f), new Vector3(-0.058f, 0.014f, 0f), 0.008f, purpleGlowMaterial);
        CreateStroke(sleep, "RightSleepEye", new Vector3(0.058f, 0.014f, 0f), new Vector3(0.158f, 0.014f, 0f), 0.008f, purpleGlowMaterial);
        sleep.gameObject.SetActive(false);

        var excited = CreateGroup("Excited", eyes);
        CreateTube(excited, "LeftExcitedEye", new[] { new Vector3(-0.151f, 0.05f, 0f), new Vector3(-0.086f, 0.008f, 0f), new Vector3(-0.151f, -0.035f, 0f) }, 0.008f, purpleGlowMaterial);
        CreateTube(excited, "RightExcitedEye", new[] { new Vector3(0.151f, 0.05f, 0f), new Vector3(0.086f, 0.008f, 0f), new Vector3(0.151f, -0.035f, 0f) }, 0.008f, purpleGlowMaterial);
        excited.gameObject.SetActive(false);

        var heart = CreateGroup("Heart", eyes);
        CreateHeart(heart, "LeftHeart", -0.108f);
        CreateHeart(heart, "RightHeart", 0.108f);
        heart.localScale = new Vector3(1f, 1.5f, 1f);
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
        ear.localPosition = new Vector3(side * 0.238f, 0.844f, -0.025f);
        ear.localRotation = Quaternion.Euler(-12f, 0f, side * -9f);
        CreatePart("WhiteFinShell", ear, finMesh, whiteMaterial, Vector3.zero,
            new Vector3(0.116f, 0.208f, 0.048f));
        CreatePart("LavenderFinInset", ear, finMesh, lavenderMaterial,
            new Vector3(0f, 0.027f, 0.0245f), new Vector3(0.073f, 0.145f, 0.008f));
    }

    static void CreateHeadphone(Transform parent, string name, float side)
    {
        var cup = CreateGroup(name, parent);
        cup.localPosition = new Vector3(side * 0.302f, 0.664f, -0.007f);
        cup.localRotation = Quaternion.LookRotation(new Vector3(side * 0.86f, 0f, 0.51f), Vector3.up);
        CreatePart("SoftEarPad", cup, sphereMesh, lavenderMaterial,
            new Vector3(0f, 0f, -0.019f), new Vector3(0.155f, 0.163f, 0.08f));
        CreatePart("BlackEarCupDisc", cup, sphereMesh, darkMaterial,
            Vector3.zero, new Vector3(0.18f, 0.18f, 0.078f));
        CreatePart("InsetDisc", cup, sphereMesh, glassMaterial,
            new Vector3(0f, 0f, 0.036f), new Vector3(0.113f, 0.113f, 0.018f));
        CreatePart("PurpleGlowRing", cup, torusMesh, purpleGlowMaterial,
            new Vector3(0f, 0f, 0.041f), new Vector3(0.126f, 0.126f, 0.086f));
    }

    static void CreateSleeve(Transform outfit, string name, float side)
    {
        var sleeve = CreateGroup(name, outfit);
        sleeve.localPosition = new Vector3(side * 0.205f, 0.338f, 0f);
        sleeve.localRotation = Quaternion.Euler(0f, 0f, side * 24f);
        CreatePart("PuffySleeve", sleeve, sphereMesh, whiteMaterial,
            Vector3.zero, new Vector3(0.127f, 0.165f, 0.155f));
        CreatePart("PurplePanelStripe", sleeve, detailBoxMesh, purpleMaterial,
            new Vector3(0f, -0.006f, 0.072f), new Vector3(0.078f, 0.085f, 0.02f));
        CreatePart("RoundedCuff", sleeve, sphereMesh, purpleMaterial,
            new Vector3(0f, -0.061f, 0f), new Vector3(0.112f, 0.047f, 0.127f));
    }

    static void CreateLogo(Transform outfit)
    {
        var z = 0.125f;
        var r = 0.0046f;
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
        start.x = -(start.x - 0.008f) * 1.3f;
        end.x = -(end.x - 0.008f) * 1.3f;
        start.y = 0.351f + (start.y - 0.506f) * 1.3f;
        end.y = 0.351f + (end.y - 0.506f) * 1.3f;
        CreateStroke(parent, name, start, end, radius, purpleMaterial);
    }

    static void CreateStroke(Transform parent, string name, Vector3 start, Vector3 end, float radius, Material material)
    {
        CreateTube(parent, name, new[] { start, end }, radius, material);
    }

    static void CreateTube(Transform parent, string name, IList<Vector3> points, float radius, Material material)
    {
        var mesh = SaveMeshAsset(name + "Tube", CreateTubeMesh(points, radius));
        var part = CreatePart(name, parent, mesh, material, Vector3.zero, Vector3.one);
        part.GetComponent<MeshRenderer>().shadowCastingMode = ShadowCastingMode.Off;
    }

    static Mesh CreateTubeMesh(IList<Vector3> points, float radius)
    {
        const int sides = 8;
        var centers = new List<Vector3>();
        var radii = new List<float>();
        var firstDirection = (points[1] - points[0]).normalized;
        centers.Add(points[0] - firstDirection * radius);
        radii.Add(0f);
        centers.Add(points[0] - firstDirection * radius * 0.7071f);
        radii.Add(radius * 0.7071f);
        foreach (var point in points)
        {
            centers.Add(point);
            radii.Add(radius);
        }
        var lastDirection = (points[points.Count - 1] - points[points.Count - 2]).normalized;
        centers.Add(points[points.Count - 1] + lastDirection * radius * 0.7071f);
        radii.Add(radius * 0.7071f);
        centers.Add(points[points.Count - 1] + lastDirection * radius);
        radii.Add(0f);
        var vertices = new List<Vector3>();
        var triangles = new List<int>();
        for (var ring = 0; ring < centers.Count; ring++)
        {
            var tangent = (centers[Mathf.Min(ring + 1, centers.Count - 1)] - centers[Mathf.Max(0, ring - 1)]).normalized;
            var normal = Vector3.Cross(tangent, Vector3.forward).normalized;
            for (var side = 0; side < sides; side++)
            {
                var angle = side * Mathf.PI * 2f / sides;
                vertices.Add(centers[ring] + radii[ring] * (normal * Mathf.Cos(angle) + Vector3.forward * Mathf.Sin(angle)));
            }
        }
        for (var ring = 0; ring < centers.Count - 1; ring++)
        {
            for (var side = 0; side < sides; side++)
            {
                var a = ring * sides + side;
                var b = ring * sides + (side + 1) % sides;
                var c = b + sides;
                var d = a + sides;
                var outward = (vertices[a] + vertices[b] + vertices[c] + vertices[d]) * 0.25f - (centers[ring] + centers[ring + 1]) * 0.5f;
                AddTriangleOutward(vertices, triangles, a, b, c, outward);
                AddTriangleOutward(vertices, triangles, a, c, d, outward);
            }
        }
        var mesh = new Mesh { vertices = vertices.ToArray() };
        mesh.SetTriangles(triangles, 0);
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
        return mesh;
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
        const int previewLayer = 30;
        var oldAmbientMode = RenderSettings.ambientMode;
        var oldAmbientLight = RenderSettings.ambientLight;
        var oldAmbientIntensity = RenderSettings.ambientIntensity;
        var oldAmbientProbe = RenderSettings.ambientProbe;
        var oldSun = RenderSettings.sun;
        var oldActiveRenderTexture = RenderTexture.active;
        var oldAsyncCompilation = ShaderUtil.allowAsyncCompilation;
        var previousLightStates = new Dictionary<Light, bool>();
        var previousLayers = new Dictionary<GameObject, int>();
        var studioObjects = new List<GameObject>();
        RenderTexture renderTexture = null;
        Texture2D capture = null;
        try
        {
            ShaderUtil.allowAsyncCompilation = false;
            foreach (var sceneLight in UnityEngine.Object.FindObjectsByType<Light>(FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                previousLightStates[sceneLight] = sceneLight.enabled;
                sceneLight.enabled = false;
            }
            foreach (var child in root.GetComponentsInChildren<Transform>(true))
            {
                previousLayers[child.gameObject] = child.gameObject.layer;
                child.gameObject.layer = previewLayer;
            }
            var cameraObject = new GameObject("ChibiPreviewCamera");
            studioObjects.Add(cameraObject);
            var camera = cameraObject.AddComponent<Camera>();
            camera.enabled = false;
            camera.orthographic = true;
            camera.orthographicSize = 0.625f;
            camera.aspect = 1f;
            camera.nearClipPlane = 0.05f;
            camera.farClipPlane = 20f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0f, 0f, 0f, 0f);
            camera.cullingMask = 1 << previewLayer;
            camera.allowHDR = true;
            var key = CreatePreviewLight("ChibiPreviewKeyLight", new Color(1f, 0.985f, 0.97f), 0.80f);
            var fill = CreatePreviewLight("ChibiPreviewFillLight", new Color(0.97f, 0.98f, 1f), 0.22f);
            var rim = CreatePreviewLight("ChibiPreviewRimLight", Color.white, 0.40f);
            studioObjects.Add(key.gameObject);
            studioObjects.Add(fill.gameObject);
            studioObjects.Add(rim.gameObject);
            RenderSettings.sun = key;
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.44f, 0.44f, 0.44f);
            RenderSettings.ambientIntensity = 1f;
            // Explicit neutral SH avoids carrying the template sky's purple bounce into frame one.
            var ambientProbe = new SphericalHarmonicsL2();
            ambientProbe.AddAmbientLight(new Color(0.30f, 0.30f, 0.30f));
            RenderSettings.ambientProbe = ambientProbe;
            renderTexture = new RenderTexture(PreviewSize, PreviewSize, 24, RenderTextureFormat.ARGBHalf, RenderTextureReadWrite.Linear)
            {
                antiAliasing = 4,
                name = "GJH Chibi HDR Studio"
            };
            renderTexture.Create();
            camera.targetTexture = renderTexture;
            capture = new Texture2D(PreviewSize, PreviewSize, TextureFormat.RGBAFloat, false, true);
            var target = new Vector3(0f, 0.521f, 0f);
            RenderView(camera, new Vector3(0f, 0.70f, 3.5f), target, "front", capture, key, fill, rim);
            RenderView(camera, new Vector3(3.5f, 0.70f, 0f), target, "side", capture, key, fill, rim);
            RenderView(camera, new Vector3(0f, 0.70f, -3.5f), target, "back", capture, key, fill, rim);
            RenderView(camera, new Vector3(2.55f, 0.98f, 3.4f), target, "3q", capture, key, fill, rim);
        }
        finally
        {
            RenderTexture.active = oldActiveRenderTexture;
            if (capture != null)
                UnityEngine.Object.DestroyImmediate(capture);
            if (renderTexture != null)
            {
                renderTexture.Release();
                UnityEngine.Object.DestroyImmediate(renderTexture);
            }
            foreach (var studioObject in studioObjects)
                UnityEngine.Object.DestroyImmediate(studioObject);
            foreach (var pair in previousLightStates)
                if (pair.Key != null)
                    pair.Key.enabled = pair.Value;
            foreach (var pair in previousLayers)
                if (pair.Key != null)
                    pair.Key.layer = pair.Value;
            RenderSettings.sun = oldSun;
            RenderSettings.ambientMode = oldAmbientMode;
            RenderSettings.ambientLight = oldAmbientLight;
            RenderSettings.ambientIntensity = oldAmbientIntensity;
            RenderSettings.ambientProbe = oldAmbientProbe;
            ShaderUtil.allowAsyncCompilation = oldAsyncCompilation;
        }
    }

    static Light CreatePreviewLight(string name, Color color, float intensity)
    {
        var lightObject = new GameObject(name);
        var light = lightObject.AddComponent<Light>();
        light.type = LightType.Directional;
        light.color = color;
        light.intensity = intensity;
        light.shadows = LightShadows.Soft;
        light.shadowStrength = 0.25f;
        light.shadowBias = 0.015f;
        light.shadowNormalBias = 0.02f;
        light.cullingMask = 1 << 30;
        return light;
    }

    static void RenderView(Camera camera, Vector3 position, Vector3 target, string fileName,
        Texture2D capture, Light key, Light fill, Light rim)
    {
        camera.transform.SetPositionAndRotation(position, Quaternion.LookRotation(target - position, Vector3.up));
        // The softbox rig follows the turntable, keeping the shell equally white in all views.
        key.transform.rotation = Quaternion.LookRotation(camera.transform.rotation * new Vector3(0.5f, -0.7f, 1f));
        fill.transform.rotation = Quaternion.LookRotation(camera.transform.rotation * new Vector3(-0.65f, -0.15f, 1f));
        rim.transform.rotation = Quaternion.LookRotation(camera.transform.rotation * new Vector3(-0.5f, -0.3f, -1f));
        // Warm up the material constants and SRP resources before reading any frame.
        for (var warmup = 0; warmup < 4; warmup++)
        {
            if (GraphicsSettings.currentRenderPipeline != null)
            {
                var request = new RenderPipeline.StandardRequest
                {
                    destination = camera.targetTexture,
                    face = CubemapFace.Unknown,
                    mipLevel = 0
                };
                if (!RenderPipeline.SupportsRenderRequest(camera, request))
                    throw new InvalidOperationException("The active render pipeline does not support standard render requests.");
                RenderPipeline.SubmitRenderRequest(camera, request);
            }
            else
                camera.Render();
        }
        var previous = RenderTexture.active;
        try
        {
            RenderTexture.active = camera.targetTexture;
            capture.ReadPixels(new Rect(0, 0, PreviewSize, PreviewSize), 0, 0, false);
            capture.Apply(false, false);
            WriteStudioImage(camera, capture, Path.Combine("Previews", fileName + ".png"));
        }
        finally
        {
            RenderTexture.active = previous;
        }
        Debug.Log($"[ChibiBuilder] Rendered Previews/{fileName}.png");
    }

    static void WriteStudioImage(Camera camera, Texture2D capture, string path)
    {
        // Deterministic HDR bloom and a seamless studio sweep, with no texture assets or floor horizon.
        const int bloomSize = PreviewSize / 4;
        var pixels = capture.GetPixels();
        var glow = new Color[bloomSize * bloomSize];
        for (var y = 0; y < PreviewSize; y++)
        {
            for (var x = 0; x < PreviewSize; x++)
            {
                var color = pixels[y * PreviewSize + x];
                var peak = Mathf.Max(color.r, color.b);
                if (peak > 1.05f && color.b > color.g * 1.3f && color.r > color.g * 1.15f)
                    glow[(y / 4) * bloomSize + x / 4] += color * (Mathf.Min(peak - 1.05f, 3f) / peak / 16f);
            }
        }
        var tightGlow = BlurGlow(glow, bloomSize, 2, 1.2f);
        var wideGlow = BlurGlow(glow, bloomSize, 7, 3.6f);
        var top = ParseColor("#E8DFF5").linear;
        var bottom = ParseColor("#F8F5FC").linear;
        var shadowColor = ParseColor("#9C8BB5").linear;
        var foot = camera.WorldToViewportPoint(new Vector3(0f, 0.007f, 0.023f));
        var output = new Color32[pixels.Length];
        for (var y = 0; y < PreviewSize; y++)
        {
            var v = (y + 0.5f) / PreviewSize;
            for (var x = 0; x < PreviewSize; x++)
            {
                var u = (x + 0.5f) / PreviewSize;
                var background = Color.Lerp(bottom, top, v);
                var halo = Mathf.Exp(-((u - 0.42f) * (u - 0.42f) / 0.22f + (v - 0.58f) * (v - 0.58f) / 0.24f));
                background = Color.Lerp(background, Color.white, halo * 0.23f);
                var dx = (u - foot.x) / 0.155f;
                var dy = (v - foot.y) / 0.017f;
                var shadow = Mathf.Exp(-dx * dx * 1.8f - dy * dy * 1.8f) * 0.22f;
                background = Color.Lerp(background, shadowColor, shadow);
                var index = y * PreviewSize + x;
                var source = pixels[index];
                var alpha = Mathf.Clamp01(source.a);
                // Premultiplied edge pixels retain their antialiasing over the pale backdrop.
                var color = new Color(source.r, source.g, source.b) + background * (1f - alpha);
                var bloomIndex = Mathf.Min(y / 4, bloomSize - 1) * bloomSize + Mathf.Min(x / 4, bloomSize - 1);
                color += tightGlow[bloomIndex] * 0.22f + wideGlow[bloomIndex] * 0.30f;
                color.r = Mathf.Min(color.r, 1f);
                color.g = Mathf.Min(color.g, 1f);
                color.b = Mathf.Min(color.b, 1f);
                color.a = 1f;
                output[index] = color.gamma;
            }
        }
        var image = new Texture2D(PreviewSize, PreviewSize, TextureFormat.RGB24, false, false);
        try
        {
            image.SetPixels32(output);
            image.Apply(false, false);
            File.WriteAllBytes(path, image.EncodeToPNG());
        }
        finally
        {
            UnityEngine.Object.DestroyImmediate(image);
        }
    }

    static Color[] BlurGlow(Color[] source, int size, int radius, float sigma)
    {
        var temporary = new Color[source.Length];
        var result = new Color[source.Length];
        var kernel = new float[radius * 2 + 1];
        var total = 0f;
        for (var i = -radius; i <= radius; i++)
        {
            kernel[i + radius] = Mathf.Exp(-i * i / (2f * sigma * sigma));
            total += kernel[i + radius];
        }
        for (var i = 0; i < kernel.Length; i++)
            kernel[i] /= total;
        for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
                for (var i = -radius; i <= radius; i++)
                    temporary[y * size + x] += source[y * size + Mathf.Clamp(x + i, 0, size - 1)] * kernel[i + radius];
        for (var y = 0; y < size; y++)
            for (var x = 0; x < size; x++)
                for (var i = -radius; i <= radius; i++)
                    result[y * size + x] += temporary[Mathf.Clamp(y + i, 0, size - 1) * size + x] * kernel[i + radius];
        return result;
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
        cubeMesh = SaveMeshAsset("SharpCube", CreateCubeMesh());
        helmetMesh = SaveMeshAsset("SmoothHelmet", CreateRoundedBoxMesh(10, 0.42f));
        screenMesh = SaveMeshAsset("RoundedScreen", CreateRoundedScreenMesh());
        hoodieMesh = SaveMeshAsset("SoftHoodie", CreateRoundedBoxMesh(8, 0.30f));
        roundedBoxMesh = SaveMeshAsset("SoftRoundedBox", CreateRoundedBoxMesh(6, 0.30f));
        detailBoxMesh = SaveMeshAsset("SmallRoundedBox", CreateRoundedBoxMesh(4, 0.24f));
        cylinderMesh = SaveMeshAsset("LowPolyCylinder", CreateCylinderMesh(8));
        torusMesh = SaveMeshAsset("Torus", CreateTorusMesh(40, 6, 0.5f, 0.10f));
        finMesh = SaveMeshAsset("EarFin", CreateFinMesh());
        heartWedgeMesh = SaveMeshAsset("HeartWedge", CreateHeartWedgeMesh());

        whiteMaterial = SaveMaterial("White", "#F4F2FA", 0f, 0.28f, null);
        darkMaterial = SaveMaterial("NearBlack", "#2A2838", 0.05f, 0.24f, null);
        glassMaterial = SaveMaterial("GlossyFaceGlass", "#16131F", 0f, 0.78f, null);
        purpleMaterial = SaveMaterial("Purple", "#8B5CF6", 0f, 0.34f, null);
        purpleGlowMaterial = SaveMaterial("PurpleEmission", "#8B5CF6", 0f, 0.28f, "#8B5CF6");
        lavenderMaterial = SaveMaterial("LightLavender", "#D9CCF7", 0f, 0.32f, null);
        screenGlintMaterial = SaveMaterial("ScreenGlint", "#4D465E", 0f, 0.42f, null);
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
        if (material.HasProperty("_SpecColor"))
            material.SetColor("_SpecColor", new Color(0.04f, 0.04f, 0.04f, 1f));
        if (material.HasProperty("_SpecularHighlights"))
            material.SetFloat("_SpecularHighlights", name == "PurpleEmission" ? 0f : 1f);
        if (material.HasProperty("_EnvironmentReflections"))
            material.SetFloat("_EnvironmentReflections", 0f);

        if (!string.IsNullOrEmpty(emissionHex) && material.HasProperty("_EmissionColor"))
        {
            var emissionColor = ParseColor(emissionHex).linear * 2.1f;
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
            AssetDatabase.CreateAsset(generated, path);
            generated.UploadMeshData(false);
            return generated;
        }

        // Use Mesh setters so regenerated topology also invalidates the GPU buffers.
        // CopySerialized alone can leave stale or empty buffers during headless renders.
        existing.Clear();
        existing.vertices = generated.vertices;
        existing.normals = generated.normals;
        existing.triangles = generated.triangles;
        existing.bounds = generated.bounds;
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

    static Mesh CreateRoundedScreenMesh()
    {
        // Sample the rounded perimeter directly, instead of spending triangles on flat faces.
        const int cornerSteps = 6;
        const int perimeter = (cornerSteps + 1) * 4;
        var vertices = new List<Vector3>();
        var normals = new List<Vector3>();
        var triangles = new List<int>();
        var angles = new[] { 90f, 60f, 30f, 0f, 0f, -30f, -60f, -90f };
        for (var ring = 0; ring < angles.Length; ring++)
        {
            var angle = angles[ring] * Mathf.Deg2Rad;
            var inset = 0.07f * (1f - Mathf.Cos(angle));
            var z = (ring < 4 ? 0.28f : -0.28f) + 0.22f * Mathf.Sin(angle);
            for (var corner = 0; corner < 4; corner++)
            {
                var center = new Vector2(corner == 0 || corner == 3 ? 0.22f : -0.22f,
                    corner < 2 ? 0.22f : -0.22f);
                for (var step = 0; step <= cornerSteps; step++)
                {
                    var theta = (corner * 90f + step * 90f / cornerSteps) * Mathf.Deg2Rad;
                    var outward = new Vector2(Mathf.Cos(theta), Mathf.Sin(theta));
                    var point = center + outward * (0.28f - inset);
                    vertices.Add(new Vector3(point.x, point.y, z));
                    normals.Add(new Vector3(outward.x * Mathf.Cos(angle), outward.y * Mathf.Cos(angle), Mathf.Sin(angle)));
                }
            }
        }
        for (var ring = 0; ring < angles.Length - 1; ring++)
        {
            for (var point = 0; point < perimeter; point++)
            {
                var a = ring * perimeter + point;
                var b = ring * perimeter + (point + 1) % perimeter;
                var c = b + perimeter;
                var d = a + perimeter;
                var normal = normals[a] + normals[b] + normals[c] + normals[d];
                AddTriangleOutward(vertices, triangles, a, b, c, normal);
                AddTriangleOutward(vertices, triangles, a, c, d, normal);
            }
        }
        foreach (var front in new[] { true, false })
        {
            var normal = front ? Vector3.forward : Vector3.back;
            var centerIndex = vertices.Count;
            vertices.Add(normal * 0.5f);
            normals.Add(normal);
            var start = front ? 0 : (angles.Length - 1) * perimeter;
            for (var point = 0; point < perimeter; point++)
                AddTriangleOutward(vertices, triangles, centerIndex, start + point, start + (point + 1) % perimeter, normal);
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
        var vertices = new[]
        {
            new Vector3(-0.5f, 0f, 0.5f), new Vector3(0.5f, 0f, 0.5f), new Vector3(0f, 1f, 0.5f),
            new Vector3(-0.5f, 0f, -0.5f), new Vector3(0.5f, 0f, -0.5f), new Vector3(0f, 1f, -0.5f)
        };
        var triangles = new[]
        {
            0, 1, 2, 5, 4, 3,
            0, 5, 3, 0, 2, 5,
            1, 4, 5, 1, 5, 2,
            0, 3, 4, 0, 4, 1
        };
        var mesh = new Mesh { vertices = vertices };
        mesh.triangles = triangles;
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
        return mesh;
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
        var mesh = new Mesh { vertices = vertices };
        mesh.triangles = triangles;
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();
        return mesh;
    }
}
