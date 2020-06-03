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

// Cubemap
uniform samplerCube environmentCubeTexture;
uniform mat3 viewToWorldRotationTransform;

// Textures
uniform sampler2D diffuseTexture;
uniform sampler2D specularTexture;

out vec4 fragmentColor;

vec3 reflectivity = vec3(0.4, 0.4, 0.4);

vec3 fresnelSchick(vec3 r0, float cosAngle)
{
    return r0 + (vec3(1.0) - r0) * pow(1.0 - cosAngle, 5.0);
}

void main()
{
    // Load base values from textures
    vec3 baseDiffuse = texture(diffuseTexture, v2f_texCoord).xyz;
    vec3 baseSpecular = texture(specularTexture, v2f_texCoord).xyz;

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

    vec3 outgoingLight = (incomingLight + ambientLight) * baseDiffuse;
    outgoingLight = outgoingLight + (incomingLight * specularIntensity * fresnelSpecular);
    outgoingLight = outgoingLight + (envSample * fresnelSpecularEye);
    fragmentColor = vec4(outgoingLight, 1.0);

    fragmentColor = vec4((incomingLight + ambientLight) * baseDiffuse + (envSample * fresnelSpecularEye), 1.0);
}