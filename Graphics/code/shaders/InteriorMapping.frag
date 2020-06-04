#version 330

// Passed in from vertex shader
in VertexData
{
	vec3 v2f_viewSpaceNormal;
	vec3 v2f_viewSpacePosition;
	vec2 v2f_texCoord;
};

// Lighting information
uniform vec3 sunPosition;
uniform vec3 sunColor;
uniform vec3 ambientColor;
uniform float ambientStrength;

float specular_exponent = 32;
vec3 reflectivity = vec3(1.0, 1.0, 1.0);

// Cubemap
uniform samplerCube environmentCubeTexture;
uniform mat3 viewToWorldRotationTransform;

// Textures
uniform sampler2D diffuseTexture;
uniform sampler2D specularTexture;

// Camera position
uniform vec3 cameraPosition;
uniform mat3 worldToModelTransform;

// Interior meta data
vec3 wallFrequencies = vec3(0.1, 0.2, 0.05);

out vec4 fragmentColor;

vec4 interiorColor()
{
	// Calculate the camera position and direction
	// This is where things are going wrong lol
	vec3 position = v2f_viewSpacePosition;
	vec3 cameraPosition = worldToModelTransform * cameraPosition;
	vec3 direction = position - cameraPosition;
	
	// Calculate wall locations
	vec3 walls = (floor(position * wallFrequencies) + step(vec3(0, 0, 0), direction)) / wallFrequencies;

	// How much of a ray is needed to reach the walls?
	vec3 rayFractions = (vec3(walls.x, walls.y, walls.z) - cameraPosition) / direction;

	// Pick normals for each wall
	vec3 signs = step(direction, vec3(0, 0, 0)) * 2 - 1;
	vec3 normalX = vec3(1, 0, 0) * signs.x;
	vec3 normalY = vec3(0, 1, 0) * signs.y;
	vec3 normalZ = vec3(0, 0, 1) * signs.z;

	// Get the closest wall
	// There's some black magic stuff going on here
	float xVSy = step(rayFractions.x, rayFractions.y);
	float rayFraction_xVSy = mix(rayFractions.y, rayFractions.x, xVSy);
	vec3 interiorNormal = mix(normalY, normalX, xVSy);
	interiorNormal = mix(normalZ, interiorNormal, step(rayFraction_xVSy, rayFractions.z));

	float lightStrength = dot(interiorNormal, vec3(0.5, 0.33166, 0.8));
	return clamp(lightStrength, 0.0, 1.0) * vec4(1, 1, 0.9, 1) + vec4(0.3, 0.3, 0.4, 1);
}

vec3 fresnelSchick(vec3 r0, float cosAngle)
{
    return r0 + (vec3(1.0) - r0) * pow(1.0 - cosAngle, 5.0);
}

void main()
{
    // Load base values from textures
    vec3 baseDiffuse = texture(diffuseTexture, v2f_texCoord).xyz;
    vec3 baseSpecular = texture(specularTexture, v2f_texCoord).xyz;
	float specularAlpha = texture(specularTexture, v2f_texCoord).a;

    // Ambient lighting
    vec3 ambientLight = ambientStrength * ambientColor;

    // Diffuse lighting
    vec3 viewSpaceDirToLight = normalize(sunPosition - v2f_viewSpacePosition);
    vec3 viewSpaceNormal = normalize(v2f_viewSpaceNormal);
    float incomingIntensity = max(0.0, dot(viewSpaceNormal, viewSpaceDirToLight));
    vec3 incomingLight = incomingIntensity * sunColor;

    // Specular lighting
    vec3 viewSpaceDirToEye = normalize(-v2f_viewSpacePosition);
    vec3 halfVector = normalize(viewSpaceDirToEye + viewSpaceDirToLight);
    float specularIntensity = max(0.0, dot(halfVector, viewSpaceNormal));
    specularIntensity = pow(specularIntensity, specular_exponent);
    vec3 fresnelSpecular = fresnelSchick(baseSpecular, max(0.0, dot(viewSpaceDirToLight, halfVector)));

    // Environment map
    vec3 worldSpaceReflectionDir = viewToWorldRotationTransform * reflect(-viewSpaceDirToEye, viewSpaceNormal);
    vec3 envSample = texture(environmentCubeTexture, worldSpaceReflectionDir).xyz;
    vec3 fresnelSpecularEye = reflectivity * fresnelSchick(baseSpecular, max(0.0, dot(viewSpaceDirToEye, viewSpaceNormal)));

	// Interior color
	vec4 interior = interiorColor();


    vec3 outgoingLight = (incomingLight + ambientLight) * baseDiffuse;
    outgoingLight = outgoingLight + (incomingLight * specularIntensity * fresnelSpecular);
    outgoingLight = outgoingLight + (envSample * fresnelSpecularEye);

	fragmentColor = mix(vec4(outgoingLight, 1.0), interior, specularAlpha);
}