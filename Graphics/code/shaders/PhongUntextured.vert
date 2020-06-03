#version 330

in vec3 positionAttribute;
in vec3	normalAttribute;
in vec2	texCoordAttribute;

uniform mat4 modelToClipTransform;
uniform mat4 modelToViewTransform;
uniform mat3 modelToViewNormalTransform;

out VertexData
{
	vec3 v2f_viewSpaceNormal;
	vec3 v2f_viewSpacePosition;
	vec2 v2f_texCoord;
};

void main() 
{
	gl_Position = modelToClipTransform * vec4(positionAttribute, 1.0);
	v2f_viewSpaceNormal = normalize(modelToViewNormalTransform * normalAttribute);
	v2f_viewSpacePosition = (modelToViewTransform * vec4(positionAttribute, 1.0)).xyz;
	v2f_texCoord = texCoordAttribute;
}
