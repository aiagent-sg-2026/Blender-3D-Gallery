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
    static Material previewGroundMaterial;

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
        root.transform.position = Vector3.zero;
        root.transform.rotation = Quaternion.identity;
        root.transform.localScale = Vector3.one;

        var head = CreateGroup("Head", root.transform);
        CreatePart("HelmetShell", head, sphereMesh, whiteMaterial,
            new Vector3(0f, 0.668f, 0f), new Vector3(0.53f, 0.45f, 0.39f));

        var face = CreateGroup("Face", root.transform);
        CreatePart("ScreenBezel", face, roundedBoxMesh, darkMaterial,
            new Vector3(0f, 0.675f, 0.175f), new Vector3(0.43f, 0.285f, 0.075f));
        CreatePart("GlossyFaceScreen", face, roundedBoxMesh, glassMaterial,
            new Vector3(0f, 0.675f, 0.211f), new Vector3(0.403f, 0.258f, 0.026f));
        var eyes = CreateGroup("Eyes", face);
        eyes.localPosition = new Vector3(0f, 0.675f, 0.226f);
        CreateExpressions(eyes);

        var ears = CreateGroup("Ears", root.transform);
        CreateEar(ears, "LeftEarFin", -1f);
        CreateEar(ears, "RightEarFin", 1f);

        var headphones = CreateGroup("Headphones", root.transform);
        CreateHeadphone(headphones, "LeftHeadphone", -1f);
        CreateHeadphone(headphones, "RightHeadphone", 1f);

        var outfit = CreateGroup("Outfit", root.transform);
        CreatePart("HoodieTorso", outfit, roundedBoxMesh, whiteMaterial,
            new Vector3(0f, 0.303f, 0f), new Vector3(0.32f, 0.225f, 0.235f));
        CreatePart("HoodShell", outfit, sphereMesh, lavenderMaterial,
            new Vector3(0f, 0.401f, -0.095f), new Vector3(0.245f, 0.14f, 0.13f));
        CreatePart("HoodCollar", outfit, torusMesh, purpleMaterial,
            new Vector3(0f, 0.412f, 0.01f), new Vector3(0.225f, 0.185f, 0.225f),
            Quaternion.Euler(90f, 0f, 0f));
        CreateSleeve(outfit, "LeftSleeve", -1f);
        CreateSleeve(outfit, "RightSleeve", 1f);
        CreatePart("KangarooPocket", outfit, roundedBoxMesh, whiteMaterial,
            new Vector3(0f, 0.241f, 0.119f), new Vector3(0.165f, 0.052f, 0.015f));
        CreateLogo(outfit);

        var legs = CreateGroup("Legs", root.transform);
        CreatePart("LeftLeg", legs, roundedBoxMesh, whiteMaterial,
            new Vector3(-0.084f, 0.115f, 0f), new Vector3(0.13f, 0.15f, 0.145f));
        CreatePart("RightLeg", legs, roundedBoxMesh, whiteMaterial,
            new Vector3(0.084f, 0.115f, 0f), new Vector3(0.13f, 0.15f, 0.145f));
        CreatePart("LeftLegPatch", legs, roundedBoxMesh, purpleMaterial,
            new Vector3(-0.084f, 0.11f, 0.075f), new Vector3(0.048f, 0.048f, 0.012f));
        CreatePart("RightLegPatch", legs, roundedBoxMesh, purpleMaterial,
            new Vector3(0.084f, 0.11f, 0.075f), new Vector3(0.048f, 0.048f, 0.012f));

        CreatePart("ShortsHem", outfit, roundedBoxMesh, purpleMaterial,
            new Vector3(0f, 0.195f, 0f), new Vector3(0.295f, 0.038f, 0.205f));
        CreatePart("Shorts", outfit, roundedBoxMesh, darkMaterial,
            new Vector3(0f, 0.215f, 0f), new Vector3(0.30f, 0.075f, 0.21f));

        var hands = CreateGroup("Hands", root.transform);
        CreatePart("LeftMitten", hands, sphereMesh, darkMaterial,
            new Vector3(-0.235f, 0.255f, 0.025f), new Vector3(0.10f, 0.095f, 0.105f));
        CreatePart("RightMitten", hands, sphereMesh, darkMaterial,
            new Vector3(0.235f, 0.255f, 0.025f), new Vector3(0.10f, 0.095f, 0.105f));

        var feet = CreateGroup("Feet", root.transform);
        CreatePart("LeftShoe", feet, sphereMesh, darkMaterial,
            new Vector3(-0.087f, 0.0375f, 0.035f), new Vector3(0.145f, 0.075f, 0.17f));
        CreatePart("RightShoe", feet, sphereMesh, darkMaterial,
            new Vector3(0.087f, 0.0375f, 0.035f), new Vector3(0.145f, 0.075f, 0.17f));

        return root;
    }

    static void CreateExpressions(Transform eyes)
    {
        var happy = CreateGroup("Happy", eyes);
        CreateStroke(happy, "LeftHappyArcA", new Vector3(-0.105f, -0.008f, 0f), new Vector3(-0.068f, 0.041f, 0f), 0.009f, purpleGlowMaterial);
        CreateStroke(happy, "LeftHappyArcB", new Vector3(-0.068f, 0.041f, 0f), new Vector3(-0.031f, -0.008f, 0f), 0.009f, purpleGlowMaterial);
        CreateStroke(happy, "RightHappyArcA", new Vector3(0.031f, -0.008f, 0f), new Vector3(0.068f, 0.041f, 0f), 0.009f, purpleGlowMaterial);
        CreateStroke(happy, "RightHappyArcB", new Vector3(0.068f, 0.041f, 0f), new Vector3(0.105f, -0.008f, 0f), 0.009f, purpleGlowMaterial);
        CreateStroke(happy, "Smile", new Vector3(-0.032f, -0.05f, 0f), new Vector3(0f, -0.06f, 0f), 0.0045f, purpleGlowMaterial);
        CreateStroke(happy, "SmileEnd", new Vector3(0f, -0.06f, 0f), new Vector3(0.032f, -0.05f, 0f), 0.0045f, purpleGlowMaterial);
        happy.gameObject.SetActive(true);

        var sleep = CreateGroup("Sleep", eyes);
        CreateStroke(sleep, "LeftSleepEye", new Vector3(-0.105f, 0.018f, 0f), new Vector3(-0.035f, 0.018f, 0f), 0.009f, purpleGlowMaterial);
        CreateStroke(sleep, "RightSleepEye", new Vector3(0.035f, 0.018f, 0f), new Vector3(0.105f, 0.018f, 0f), 0.009f, purpleGlowMaterial);
        sleep.gameObject.SetActive(false);

        var excited = CreateGroup("Excited", eyes);
        CreateStroke(excited, "LeftExcitedEyeA", new Vector3(-0.105f, 0.045f, 0f), new Vector3(-0.058f, 0.008f, 0f), 0.009f, purpleGlowMaterial);
        CreateStroke(excited, "LeftExcitedEyeB", new Vector3(-0.058f, 0.008f, 0f), new Vector3(-0.105f, -0.029f, 0f), 0.009f, purpleGlowMaterial);
        CreateStroke(excited, "RightExcitedEyeA", new Vector3(0.105f, 0.045f, 0f), new Vector3(0.058f, 0.008f, 0f), 0.009f, purpleGlowMaterial);
        CreateStroke(excited, "RightExcitedEyeB", new Vector3(0.058f, 0.008f, 0f), new Vector3(0.105f, -0.029f, 0f), 0.009f, purpleGlowMaterial);
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
        var rotation = Quaternion.Euler(-10f, 0f, side * -10f);
        var ear = CreateGroup(name, parent);
        ear.localPosition = new Vector3(side * 0.19f, 0.794f, -0.025f);
        ear.localRotation = rotation;
        CreatePart("OuterFin", ear, finMesh, whiteMaterial, Vector3.zero,
            new Vector3(0.12f, 0.215f, 0.055f));
        CreatePart("InnerFin", ear, finMesh, lavenderMaterial,
            new Vector3(0f, 0.027f, 0.029f), new Vector3(0.068f, 0.145f, 0.005f));
    }

    static void CreateHeadphone(Transform parent, string name, float side)
    {
        var normal = new Vector3(side * 0.82f, 0f, 0.57f).normalized;
        var center = new Vector3(side * 0.246f, 0.665f, 0.025f);
        CreatePart(name + "Cup", parent, cylinderMesh, darkMaterial, center,
            new Vector3(0.16f, 0.055f, 0.16f), Quaternion.FromToRotation(Vector3.up, normal));
        CreatePart(name + "GlowRing", parent, torusMesh, purpleGlowMaterial,
            center + normal * 0.029f, new Vector3(0.119f, 0.119f, 0.119f),
            Quaternion.LookRotation(normal, Vector3.up));
    }

    static void CreateSleeve(Transform outfit, string name, float side)
    {
        CreatePart(name, outfit, sphereMesh, whiteMaterial,
            new Vector3(side * 0.18f, 0.319f, 0f), new Vector3(0.12f, 0.15f, 0.16f),
            Quaternion.Euler(0f, 0f, side * -22f));
        CreatePart(name + "PurplePanel", outfit, roundedBoxMesh, purpleMaterial,
            new Vector3(side * 0.193f, 0.32f, 0.073f), new Vector3(0.052f, 0.072f, 0.016f),
            Quaternion.Euler(0f, 0f, side * -22f));
    }

    static void CreateLogo(Transform outfit)
    {
        var z = 0.127f;
        var r = 0.005f;
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
        start.x = -start.x * 1.17f;
        end.x = -end.x * 1.17f;
        start.y -= 0.18f;
        end.y -= 0.18f;
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
        var oldActiveRenderTexture = RenderTexture.active;
        var previousLightStates = new Dictionary<Light, bool>();
        GameObject cameraObject = null;
        GameObject keyLightObject = null;
        GameObject fillLightObject = null;
        RenderTexture renderTexture = null;
        Texture2D capture = null;

        try
        {
            foreach (var sceneLight in UnityEngine.Object.FindObjectsByType<Light>(FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                previousLightStates[sceneLight] = sceneLight.enabled;
                sceneLight.enabled = false;
            }

            cameraObject = new GameObject("ChibiPreviewCamera");
            var camera = cameraObject.AddComponent<Camera>();
            camera.enabled = false;
            camera.orthographic = true;
            camera.orthographicSize = 0.61f;
            camera.aspect = 1f;
            camera.nearClipPlane = 0.05f;
            camera.farClipPlane = 20f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0f, 0f, 0f, 0f);
            camera.cullingMask = ~0;
            camera.allowHDR = true;

            keyLightObject = CreatePreviewLight("ChibiPreviewKeyLight", Color.white, 0.75f,
                Quaternion.Euler(25f, 205f, 0f), false);
            fillLightObject = CreatePreviewLight("ChibiPreviewFillLight", Color.white, 0.35f,
                Quaternion.Euler(20f, 135f, 0f), false);
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.55f, 0.55f, 0.55f);
            RenderSettings.ambientIntensity = 1f;

            renderTexture = new RenderTexture(PreviewSize, PreviewSize, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB)
            {
                antiAliasing = 4,
                name = "GJH Chibi Preview RenderTexture"
            };
            renderTexture.Create();
            camera.targetTexture = renderTexture;
            capture = new Texture2D(PreviewSize, PreviewSize, TextureFormat.RGBA32, false, false);

            // The first URP render warms material variants before saving the final views.
            RenderView(camera, new Vector3(3.2f, 0.70f, 0f), new Vector3(0f, 0.50f, 0f), "side", capture);
            RenderView(camera, new Vector3(3.2f, 0.70f, 0f), new Vector3(0f, 0.50f, 0f), "side", capture);
            RenderView(camera, new Vector3(0f, 0.70f, -3.2f), new Vector3(0f, 0.50f, 0f), "back", capture);
            RenderView(camera, new Vector3(2.55f, 0.82f, 2.95f), new Vector3(0f, 0.50f, 0f), "3q", capture);
            RenderView(camera, new Vector3(0f, 0.70f, 3.2f), new Vector3(0f, 0.50f, 0f), "front", capture);
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
            if (cameraObject != null)
                UnityEngine.Object.DestroyImmediate(cameraObject);
            if (keyLightObject != null)
                UnityEngine.Object.DestroyImmediate(keyLightObject);
            if (fillLightObject != null)
                UnityEngine.Object.DestroyImmediate(fillLightObject);
            foreach (var pair in previousLightStates)
                if (pair.Key != null)
                    pair.Key.enabled = pair.Value;
            RenderSettings.ambientMode = oldAmbientMode;
            RenderSettings.ambientLight = oldAmbientLight;
            RenderSettings.ambientIntensity = oldAmbientIntensity;
        }
    }

    static GameObject CreatePreviewLight(string name, Color color, float intensity, Quaternion rotation, bool shadows)
    {
        var lightObject = new GameObject(name);
        var light = lightObject.AddComponent<Light>();
        light.type = LightType.Directional;
        light.color = color;
        light.intensity = intensity;
        light.shadows = shadows ? LightShadows.Soft : LightShadows.None;
        light.shadowStrength = 0.35f;
        light.cullingMask = ~0;
        lightObject.transform.rotation = rotation;
        return lightObject;
    }

    static void RenderView(Camera camera, Vector3 position, Vector3 target, string fileName, Texture2D capture)
    {
        camera.transform.position = position;
        camera.transform.rotation = Quaternion.LookRotation(target - position, Vector3.up);
        if (GraphicsSettings.currentRenderPipeline != null)
        {
            var request = new UnityEngine.Rendering.RenderPipeline.StandardRequest
            {
                destination = camera.targetTexture,
                face = CubemapFace.Unknown,
                mipLevel = 0
            };
            if (!UnityEngine.Rendering.RenderPipeline.SupportsRenderRequest(camera, request))
                throw new InvalidOperationException("The active render pipeline does not support standard render requests.");
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(camera, request);
        }
        else
        {
            camera.Render();
        }
        var previous = RenderTexture.active;
        RenderTexture.active = camera.targetTexture;
        capture.ReadPixels(new Rect(0, 0, PreviewSize, PreviewSize), 0, 0, false);
        capture.Apply(false, false);
        // Composite over a continuous studio gradient, keeping the model out of the GLB background.
        var pixels = capture.GetPixels32();
        var glow = BuildPreviewGlow(pixels);
        for (var y = 0; y < PreviewSize; y++)
        {
            var t = y / (float)(PreviewSize - 1);
            var background = Color.Lerp(new Color(0.90f, 0.87f, 0.97f), new Color(0.97f, 0.96f, 1f), t);
            for (var x = 0; x < PreviewSize; x++)
            {
                var index = y * PreviewSize + x;
                var foreground = (Color)pixels[index];
                var blended = Color.Lerp(background, foreground, foreground.a);
                var halo = glow[index] * 0.7f;
                blended.r = Mathf.Clamp01(blended.r + halo * 0.60f);
                blended.g = Mathf.Clamp01(blended.g + halo * 0.24f);
                blended.b = Mathf.Clamp01(blended.b + halo * 0.95f);
                blended.a = 1f;
                pixels[index] = blended;
            }
        }
        capture.SetPixels32(pixels);
        capture.Apply(false, false);
        File.WriteAllBytes(Path.Combine("Previews", fileName + ".png"), capture.EncodeToPNG());
        RenderTexture.active = previous;
        Debug.Log($"[ChibiBuilder] Rendered Previews/{fileName}.png");
    }

    static float[] BuildPreviewGlow(Color32[] pixels)
    {
        // Blur only bright purple foreground pixels; the exported model stays texture-free.
        var mask = new float[pixels.Length];
        var horizontal = new float[pixels.Length];
        var result = new float[pixels.Length];
        for (var i = 0; i < pixels.Length; i++)
        {
            var p = pixels[i];
            if (p.a > 220 && p.r > 165 && p.b > 190 && p.r > p.g * 1.12f && p.b > p.g * 1.15f)
                mask[i] = 1f;
        }

        const int radius = 10;
        for (var y = 0; y < PreviewSize; y++)
        for (var x = 0; x < PreviewSize; x++)
        {
            float total = 0f, weight = 0f;
            for (var offset = -radius; offset <= radius; offset++)
            {
                var sampleX = Mathf.Clamp(x + offset, 0, PreviewSize - 1);
                var w = radius + 1 - Mathf.Abs(offset);
                total += mask[y * PreviewSize + sampleX] * w;
                weight += w;
            }
            horizontal[y * PreviewSize + x] = total / weight;
        }
        for (var y = 0; y < PreviewSize; y++)
        for (var x = 0; x < PreviewSize; x++)
        {
            float total = 0f, weight = 0f;
            for (var offset = -radius; offset <= radius; offset++)
            {
                var sampleY = Mathf.Clamp(y + offset, 0, PreviewSize - 1);
                var w = radius + 1 - Mathf.Abs(offset);
                total += horizontal[sampleY * PreviewSize + x] * w;
                weight += w;
            }
            result[y * PreviewSize + x] = total / weight;
        }
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
        sphereMesh = SaveMeshAsset("LowPolySphere", CreateSphereMesh(16, 12));
        cubeMesh = SaveMeshAsset("SharpCube", CreateCubeMesh());
        roundedBoxMesh = SaveMeshAsset("SoftRoundedBox", CreateRoundedBoxMesh(6, 0.30f));
        cylinderMesh = SaveMeshAsset("LowPolyCylinder", CreateCylinderMesh(16));
        torusMesh = SaveMeshAsset("Torus", CreateTorusMesh(32, 8, 0.5f, 0.12f));
        finMesh = SaveMeshAsset("EarFin", CreateFinMesh());
        heartWedgeMesh = SaveMeshAsset("HeartWedge", CreateHeartWedgeMesh());

        whiteMaterial = SaveMaterial("White", "#F4F2FA", 0f, 0.28f, null);
        darkMaterial = SaveMaterial("NearBlack", "#2A2838", 0.05f, 0.24f, null);
        glassMaterial = SaveMaterial("GlossyFaceGlass", "#100F18", 0f, 0.48f, null);
        purpleMaterial = SaveMaterial("Purple", "#8B5CF6", 0f, 0.34f, null);
        purpleGlowMaterial = SaveMaterial("PurpleEmission", "#8B5CF6", 0f, 0.28f, "#8B5CF6");
        lavenderMaterial = SaveMaterial("LightLavender", "#D9CCF7", 0f, 0.32f, null);
        previewGroundMaterial = SaveMaterial("PreviewGround", "#EEEAF5", 0f, 0.72f, null);
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
            material.SetFloat("_SpecularHighlights", 0f);
        if (material.HasProperty("_EnvironmentReflections") && (name == "GlossyFaceGlass" || name == "PurpleEmission"))
            material.SetFloat("_EnvironmentReflections", 0f);

        if (!string.IsNullOrEmpty(emissionHex) && material.HasProperty("_EmissionColor"))
        {
            var emissionColor = ParseColor(emissionHex) * 1.0f;
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
            return generated;
        }

        EditorUtility.CopySerialized(generated, existing);
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
